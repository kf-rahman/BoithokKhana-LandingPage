"""Tests for the admin orders endpoints: list, flags, correction, parse-pending."""

from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.models.menu import Menu, MenuItem, MenuStatus
from app.models.order import Order, OrderCorrection
from app.services import order_parsing
from app.services.order_parsing import ParseConfidence, ParsedItem, ParsedOrder

PIN = {"X-Admin-Pin": "1234"}


def _order(db: Session, name: str = "Asha") -> Order:
    order = Order(
        customer_name=name,
        customer_email=f"{name.lower()}@example.com",
        customer_phone="555",
        raw_text="2 chicken biryani",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def _publish_menu(db: Session) -> Menu:
    menu = Menu(
        week_of=date(2026, 6, 22),
        status=MenuStatus.published.value,
        published_at=datetime.now(timezone.utc),
        items=[MenuItem(name="Chicken Biryani", price_cents=1500)],
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


def test_list_orders_requires_pin(client: TestClient, db_session: Session) -> None:
    _order(db_session)
    assert client.get("/api/admin/orders").status_code == 401


def test_list_orders_returns_all(client: TestClient, db_session: Session) -> None:
    _order(db_session, "Asha")
    _order(db_session, "Karim")
    res = client.get("/api/admin/orders", headers=PIN)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_update_flags(client: TestClient, db_session: Session) -> None:
    order = _order(db_session)
    res = client.patch(
        f"/api/admin/orders/{order.id}",
        headers=PIN,
        json={"delivered": True, "confirmation_email_sent": True},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["delivered"] is True
    assert body["confirmation_email_sent"] is True

    res2 = client.patch(
        f"/api/admin/orders/{order.id}", headers=PIN, json={"delivered": False}
    )
    assert res2.json()["delivered"] is False
    assert res2.json()["confirmation_email_sent"] is True


def test_update_flags_requires_pin(client: TestClient, db_session: Session) -> None:
    order = _order(db_session)
    assert (
        client.patch(f"/api/admin/orders/{order.id}", json={"delivered": True}).status_code
        == 401
    )


def test_update_flags_missing_order_404(client: TestClient) -> None:
    assert (
        client.patch("/api/admin/orders/999", headers=PIN, json={"delivered": True}).status_code
        == 404
    )


def test_correct_order_items(client: TestClient, db_session: Session) -> None:
    _publish_menu(db_session)
    order = _order(db_session)
    original_raw = order.raw_text

    res = client.patch(
        f"/api/admin/orders/{order.id}/items",
        headers=PIN,
        json={
            "items": [
                {"item_name": "Chicken Biryani", "quantity": 3, "notes": "extra spicy"}
            ],
            "note": "fixed by Dad",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "parsed"
    assert body["raw_text"] == original_raw  # raw text never touched
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["item_name"] == "Chicken Biryani"
    assert item["quantity"] == 3
    assert item["menu_item_id"] is not None  # re-matched to the menu
    assert item["unit_price_cents"] == 1500
    assert body["total_cents"] == 4500  # 3 × $15.00

    # The correction is audited.
    assert (
        db_session.query(OrderCorrection).filter_by(order_id=order.id).count() == 1
    )


def test_correct_requires_pin(client: TestClient, db_session: Session) -> None:
    order = _order(db_session)
    res = client.patch(
        f"/api/admin/orders/{order.id}/items",
        json={"items": [{"item_name": "X", "quantity": 1}]},
    )
    assert res.status_code == 401


def test_correct_missing_order_404(client: TestClient) -> None:
    res = client.patch(
        "/api/admin/orders/999/items",
        headers=PIN,
        json={"items": [{"item_name": "X", "quantity": 1}]},
    )
    assert res.status_code == 404


def test_parse_pending_parses_all(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    _publish_menu(db_session)
    _order(db_session, "Asha")
    _order(db_session, "Karim")

    def fake(raw_text: str, menu: Menu | None) -> ParsedOrder:
        return ParsedOrder(
            items=[ParsedItem(name="Chicken Biryani", quantity=1, modifiers=[], notes=None)],
            delivery_date=None,
            delivery_notes=None,
            confidence=ParseConfidence.high,
            unmatched_text=None,
        )

    monkeypatch.setattr(order_parsing, "_request_structured_parse", fake)
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")

    res = client.post("/api/admin/orders/parse-pending", headers=PIN)
    assert res.status_code == 200
    parsed = res.json()
    assert len(parsed) == 2
    assert all(o["status"] == "parsed" for o in parsed)


def test_parse_pending_no_key_503(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    _order(db_session)
    assert (
        client.post("/api/admin/orders/parse-pending", headers=PIN).status_code == 503
    )
