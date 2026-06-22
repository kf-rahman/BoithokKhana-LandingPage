"""Order-parsing tests. The Claude call is mocked via the isolated
``_request_structured_parse`` so these run offline and deterministically."""
from __future__ import annotations

from app.services import order_parsing
from app.services.order_parsing import ParsedOrder
from tests.conftest import ADMIN_HEADERS


async def _publish_menu(client, items):
    res = await client.post(
        "/api/admin/menus",
        headers=ADMIN_HEADERS,
        json={"week_start_date": "2026-06-15", "items": items, "published": True},
    )
    assert res.status_code == 201


async def _submit(client, raw):
    return (
        await client.post(
            "/api/orders",
            json={"customer_name": "A", "customer_phone": "1", "raw_text": raw},
        )
    ).json()


def _fake(**kwargs):
    def _call(raw_text, menu_item_names):
        return ParsedOrder(**kwargs)

    return _call


async def test_happy_path_parses_and_totals(client, monkeypatch):
    await _publish_menu(client, [{"name": "Chicken Biryani", "price_cents": 1200}])
    order = await _submit(client, "2 chicken biryani")
    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(
            items=[{"name": "Chicken Biryani", "quantity": 2}],
            item_confidence="high",
            delivery_confidence="high",
        ),
    )
    body = (await client.post(f"/api/admin/orders/{order['id']}/parse", headers=ADMIN_HEADERS)).json()
    assert body["status"] == "parsed"
    assert body["structured_items"][0]["matched"] is True
    assert body["structured_items"][0]["unit_price_cents"] == 1200
    assert body["total_cents"] == 2400


async def test_unmatched_text_forces_needs_review(client, monkeypatch):
    await _publish_menu(client, [{"name": "Chicken Biryani", "price_cents": 1200}])
    order = await _submit(client, "2 biryani and something weird")
    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(
            items=[{"name": "Chicken Biryani", "quantity": 2}],
            item_confidence="high",
            delivery_confidence="high",
            unmatched_text="something weird",
        ),
    )
    body = (await client.post(f"/api/admin/orders/{order['id']}/parse", headers=ADMIN_HEADERS)).json()
    assert body["status"] == "needs_review"
    assert body["unmatched_text"] == "something weird"


async def test_item_not_on_menu_forces_needs_review(client, monkeypatch):
    await _publish_menu(client, [{"name": "Chicken Biryani", "price_cents": 1200}])
    order = await _submit(client, "1 dragon stew")
    monkeypatch.setattr(
        order_parsing,
        "_request_structured_parse",
        _fake(
            items=[{"name": "Dragon Stew", "quantity": 1}],
            item_confidence="high",
            delivery_confidence="high",
        ),
    )
    body = (await client.post(f"/api/admin/orders/{order['id']}/parse", headers=ADMIN_HEADERS)).json()
    assert body["status"] == "needs_review"
    assert body["structured_items"][0]["matched"] is False
    assert body["structured_items"][0]["unit_price_cents"] is None


async def test_low_delivery_confidence_does_not_block(client, monkeypatch):
    await _publish_menu(client, [{"name": "Veg Thali", "price_cents": 1000}])
    order = await _submit(client, "1 veg thali this weekend")
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
    body = (await client.post(f"/api/admin/orders/{order['id']}/parse", headers=ADMIN_HEADERS)).json()
    assert body["status"] == "parsed"  # delivery uncertainty must not gate review
    assert body["delivery_confidence"] == "low"


async def test_parse_failure_preserves_order(client, monkeypatch):
    await _publish_menu(client, [{"name": "Veg Thali", "price_cents": 1000}])
    order = await _submit(client, "1 veg thali")

    def boom(raw_text, menu_item_names):
        raise RuntimeError("API down")

    monkeypatch.setattr(order_parsing, "_request_structured_parse", boom)
    res = await client.post(f"/api/admin/orders/{order['id']}/parse", headers=ADMIN_HEADERS)
    assert res.status_code == 502
    # The order survives untouched and stays pending for a retry.
    got = (await client.get("/api/admin/orders", headers=ADMIN_HEADERS)).json()[0]
    assert got["status"] == "pending_parse"
    assert got["raw_text"] == "1 veg thali"
    assert got["structured_items"] is None
