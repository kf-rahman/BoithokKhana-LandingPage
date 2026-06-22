"""Acceptance tests for specs/admin-dashboard.md (parser mocked)."""
from __future__ import annotations

from app.config import settings
from app.services import order_parsing
from app.services.order_parsing import ParsedOrder

ADMIN = {"X-Admin-Pin": settings.admin_pin}
ORDER = {"customer_name": "Mr Rahman", "customer_contact": "555-0001"}


def _fake(**kwargs):
    def _call(raw_text, menu_item_names):
        return ParsedOrder(**kwargs)

    return _call


def test_admin_endpoints_require_pin(client):
    assert client.get("/api/admin/orders").status_code == 401
    assert client.get("/api/admin/orders", headers={"X-Admin-Pin": "nope"}).status_code == 401
    assert client.get("/api/admin/orders", headers=ADMIN).status_code == 200


def test_publish_menu_then_current(client):
    res = client.post(
        "/api/admin/menus",
        headers=ADMIN,
        json={"week_start_date": "2026-06-22", "items": [{"name": "Chicken Biryani", "price_cents": 1200}]},
    )
    assert res.status_code == 201
    current = client.get("/api/menus/current").json()
    assert current["items"][0]["name"] == "Chicken Biryani"


def test_correction_preserves_raw_and_clears_review(client, seed_menu, monkeypatch):
    seed_menu([{"name": "Veg Thali", "price_cents": 1000}])
    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(items=[{"name": "Mystery Dish", "quantity": 1}], item_confidence="high", delivery_confidence="high"),
    )
    created = client.post("/api/orders", json={**ORDER, "raw_text": "original text"}).json()
    assert created["status"] == "needs_review"  # item not on menu

    res = client.patch(
        f"/api/admin/orders/{created['id']}",
        headers=ADMIN,
        json={"items": [{"name": "Veg Thali", "quantity": 2}], "correction_note": "fixed by Dad"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["raw_text"] == "original text"  # never changed
    assert body["status"] == "parsed"
    assert body["corrected_at"] is not None
    assert body["correction_note"] == "fixed by Dad"
    assert body["structured_items"]["items"][0]["matched"] is True
    assert body["structured_items"]["items"][0]["unit_price_cents"] == 1000


def test_parse_pending_reparses_failed_orders(client, seed_menu, monkeypatch):
    seed_menu([{"name": "Veg Thali", "price_cents": 1000}])

    def boom(raw_text, menu_item_names):
        raise RuntimeError("API down")

    monkeypatch.setattr(order_parsing, "_request_structured_parse", boom)
    client.post("/api/orders", json={**ORDER, "raw_text": "1 veg thali"})  # stays pending

    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(items=[{"name": "Veg Thali", "quantity": 1}], item_confidence="high", delivery_confidence="high"),
    )
    res = client.post("/api/admin/orders/parse-pending", headers=ADMIN)
    assert res.status_code == 200
    parsed = res.json()
    assert len(parsed) == 1
    assert parsed[0]["status"] == "parsed"


def test_csv_export_contains_order(client, seed_menu, monkeypatch):
    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(items=[], item_confidence="high", delivery_confidence="high"),
    )
    client.post("/api/orders", json={"customer_name": "Csv Person", "customer_contact": "9", "raw_text": "hi"})
    res = client.get("/api/admin/orders.csv", headers=ADMIN)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "Order ID" in res.text
    assert "Csv Person" in res.text
