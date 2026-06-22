"""Menu publishing, current-menu, CSV export, parse-pending guard."""
from __future__ import annotations

from app.services import order_parsing
from tests.conftest import ADMIN_HEADERS


async def test_publish_and_get_current_menu(client):
    res = await client.post(
        "/api/admin/menus",
        headers=ADMIN_HEADERS,
        json={
            "week_start_date": "2026-06-15",
            "items": [
                {"name": "Chicken Biryani", "price_cents": 1200},
                {"name": "Veg Thali", "price_cents": 1000},
            ],
            "published": True,
        },
    )
    assert res.status_code == 201
    current = await client.get("/api/menus/current")
    assert current.status_code == 200
    body = current.json()
    assert body is not None
    assert len(body["items"]) == 2
    assert body["items"][0]["price_cents"] == 1200


async def test_current_menu_is_null_when_none_published(client):
    current = await client.get("/api/menus/current")
    assert current.status_code == 200
    assert current.json() is None


async def test_csv_export_contains_order(client):
    await client.post(
        "/api/orders",
        json={"customer_name": "Csv Guy", "customer_phone": "9", "raw_text": "1 thali"},
    )
    res = await client.get("/api/admin/orders.csv", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "Order ID" in res.text
    assert "Csv Guy" in res.text


async def test_parse_pending_without_key_returns_503(client, monkeypatch):
    await client.post(
        "/api/orders",
        json={"customer_name": "A", "customer_phone": "1", "raw_text": "x"},
    )

    def no_key(raw_text, menu_item_names):
        raise order_parsing.ParserNotConfigured("no key")

    monkeypatch.setattr(order_parsing, "_request_structured_parse", no_key)
    res = await client.post("/api/admin/orders/parse-pending", headers=ADMIN_HEADERS)
    assert res.status_code == 503
