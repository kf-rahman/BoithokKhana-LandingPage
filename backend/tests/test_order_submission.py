"""Acceptance tests for specs/order-submission.md (parser mocked)."""
from __future__ import annotations

from app.services import order_parsing
from app.services.order_parsing import ParsedOrder

ORDER = {"customer_name": "Mr Rahman", "customer_contact": "555-0001"}


def _fake(**kwargs):
    def _call(raw_text, menu_item_names):
        return ParsedOrder(**kwargs)

    return _call


def test_empty_text_is_rejected(client):
    res = client.post("/api/orders", json={**ORDER, "raw_text": ""})
    assert res.status_code == 422


def test_high_confidence_parses_end_to_end(client, seed_menu, monkeypatch):
    seed_menu([{"name": "Chicken Biryani", "price_cents": 1200}])
    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(
            items=[{"name": "Chicken Biryani", "quantity": 2}],
            item_confidence="high",
            delivery_confidence="high",
        ),
    )
    res = client.post("/api/orders", json={**ORDER, "raw_text": "2 chicken biryani"})
    assert res.status_code == 201
    body = res.json()
    assert body["raw_text"] == "2 chicken biryani"
    assert body["status"] == "parsed"
    item = body["structured_items"]["items"][0]
    assert item["matched"] is True
    assert item["unit_price_cents"] == 1200


def test_item_not_on_menu_needs_review(client, seed_menu, monkeypatch):
    seed_menu([{"name": "Chicken Biryani", "price_cents": 1200}])
    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(
            items=[{"name": "Dragon Stew", "quantity": 1}],
            item_confidence="high",
            delivery_confidence="high",
        ),
    )
    body = client.post("/api/orders", json={**ORDER, "raw_text": "1 dragon stew"}).json()
    assert body["status"] == "needs_review"
    assert body["structured_items"]["items"][0]["matched"] is False


def test_unmatched_text_needs_review(client, seed_menu, monkeypatch):
    seed_menu([{"name": "Veg Thali", "price_cents": 1000}])
    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(
            items=[{"name": "Veg Thali", "quantity": 1}],
            item_confidence="high",
            delivery_confidence="high",
            unmatched_text="and a thing we don't sell",
        ),
    )
    body = client.post("/api/orders", json={**ORDER, "raw_text": "1 veg thali and a thing"}).json()
    assert body["status"] == "needs_review"


def test_low_delivery_confidence_does_not_gate_review(client, seed_menu, monkeypatch):
    seed_menu([{"name": "Veg Thali", "price_cents": 1000}])
    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(
            items=[{"name": "Veg Thali", "quantity": 1}],
            item_confidence="high",
            delivery_confidence="low",
            delivery_notes="this weekend",
        ),
    )
    body = client.post("/api/orders", json={**ORDER, "raw_text": "1 veg thali this weekend"}).json()
    assert body["status"] == "parsed"  # delivery uncertainty must not gate
    assert body["delivery_confidence"] == "low"


def test_parse_failure_keeps_order_pending_and_confirms(client, seed_menu, monkeypatch):
    seed_menu([{"name": "Veg Thali", "price_cents": 1000}])

    def boom(raw_text, menu_item_names):
        raise RuntimeError("API down")

    monkeypatch.setattr(order_parsing, "_request_structured_parse", boom)
    res = client.post("/api/orders", json={**ORDER, "raw_text": "1 veg thali"})
    assert res.status_code == 201  # customer still sees success
    body = res.json()
    assert body["status"] == "pending_parse"  # resolved open question
    assert body["raw_text"] == "1 veg thali"  # raw text saved
    assert body["structured_items"] is None
