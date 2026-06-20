"""Tests for order parsing (docs/stories/order-parsing.md).

The single Claude-calling function is mocked, so these run without an API key
and assert the deterministic behavior around it: menu matching, status rules,
raw-text preservation, and failure handling.
"""

from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.models.menu import Menu, MenuItem, MenuStatus
from app.models.order import Order
from app.services import order_parsing
from app.services.order_parsing import (
    OrderParseError,
    ParseConfidence,
    ParsedItem,
    ParsedOrder,
)

PIN = {"X-Admin-Pin": "1234"}


def _publish_menu(db: Session) -> Menu:
    menu = Menu(
        week_of=date(2026, 6, 22),
        status=MenuStatus.published.value,
        published_at=datetime.now(timezone.utc),
        items=[
            MenuItem(name="Chicken Biryani", price_cents=1500),
            MenuItem(name="Veg Thali", price_cents=1200),
        ],
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


def _make_order(db: Session, raw: str = "2 chicken biryani no spice, deliver friday") -> Order:
    order = Order(
        customer_name="Asha",
        customer_email="asha@example.com",
        customer_phone="555",
        raw_text=raw,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def test_parse_requires_pin(client: TestClient, db_session: Session) -> None:
    order = _make_order(db_session)
    assert client.post(f"/api/admin/orders/{order.id}/parse").status_code == 401


def test_parse_missing_order_404(client: TestClient) -> None:
    assert client.post("/api/admin/orders/999/parse", headers=PIN).status_code == 404


def test_high_confidence_parse_creates_matched_items(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    _publish_menu(db_session)
    order = _make_order(db_session)

    def fake(raw_text: str, menu: Menu | None) -> ParsedOrder:
        return ParsedOrder(
            items=[
                ParsedItem(name="Chicken Biryani", quantity=2, modifiers=["no spice"], notes=None)
            ],
            delivery_date=date(2026, 6, 26),
            delivery_notes=None,
            confidence=ParseConfidence.high,
            unmatched_text=None,
        )

    monkeypatch.setattr(order_parsing, "_request_structured_parse", fake)

    res = client.post(f"/api/admin/orders/{order.id}/parse", headers=PIN)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "parsed"
    assert body["raw_text"] == order.raw_text  # never modified
    assert body["delivery_date"] == "2026-06-26"
    assert body["confidence"] == "high"
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["item_name"] == "Chicken Biryani"
    assert item["quantity"] == 2
    assert item["menu_item_id"] is not None  # matched a real menu item
    assert item["notes"] == "no spice"


def test_item_not_on_menu_flags_review_and_is_not_invented(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    _publish_menu(db_session)
    order = _make_order(db_session, raw="1 jollof rice please")

    def fake(raw_text: str, menu: Menu | None) -> ParsedOrder:
        # Even a confident model output: if it's not on the menu, it must not be
        # accepted as a real item.
        return ParsedOrder(
            items=[ParsedItem(name="Jollof Rice", quantity=1, modifiers=[], notes=None)],
            delivery_date=None,
            delivery_notes=None,
            confidence=ParseConfidence.high,
            unmatched_text=None,
        )

    monkeypatch.setattr(order_parsing, "_request_structured_parse", fake)

    res = client.post(f"/api/admin/orders/{order.id}/parse", headers=PIN)
    body = res.json()
    assert body["status"] == "needs_review"
    assert len(body["items"]) == 1
    assert body["items"][0]["item_name"] == "Jollof Rice"  # kept, not invented
    assert body["items"][0]["menu_item_id"] is None  # not linked to a menu item


def test_low_confidence_flags_review(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    _publish_menu(db_session)
    order = _make_order(db_session)

    def fake(raw_text: str, menu: Menu | None) -> ParsedOrder:
        return ParsedOrder(
            items=[ParsedItem(name="Chicken Biryani", quantity=1, modifiers=[], notes=None)],
            delivery_date=None,
            delivery_notes=None,
            confidence=ParseConfidence.low,
            unmatched_text=None,
        )

    monkeypatch.setattr(order_parsing, "_request_structured_parse", fake)
    res = client.post(f"/api/admin/orders/{order.id}/parse", headers=PIN)
    assert res.json()["status"] == "needs_review"


def test_api_failure_keeps_raw_text_and_flags_review(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    _publish_menu(db_session)
    order = _make_order(db_session)
    original = order.raw_text

    def boom(raw_text: str, menu: Menu | None) -> ParsedOrder:
        raise OrderParseError("simulated API outage")

    monkeypatch.setattr(order_parsing, "_request_structured_parse", boom)

    res = client.post(f"/api/admin/orders/{order.id}/parse", headers=PIN)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "needs_review"
    assert body["raw_text"] == original  # never lost on failure
    assert body["items"] == []  # nothing invented

    row = db_session.get(Order, order.id)
    assert row is not None
    assert row.raw_text == original


def test_no_api_key_returns_503(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    _publish_menu(db_session)
    order = _make_order(db_session)
    res = client.post(f"/api/admin/orders/{order.id}/parse", headers=PIN)
    assert res.status_code == 503
