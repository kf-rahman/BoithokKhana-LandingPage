"""Order submission, admin auth, and correction tests."""
from __future__ import annotations

from tests.conftest import ADMIN_HEADERS


async def test_submit_persists_raw_text_as_pending(client):
    res = await client.post(
        "/api/orders",
        json={
            "customer_name": "Mr Rahman",
            "customer_phone": "555-0001",
            "raw_text": "2 chicken biryani no spice",
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "pending_parse"
    assert body["raw_text"] == "2 chicken biryani no spice"
    assert body["structured_items"] is None
    assert body["total_cents"] == 0


async def test_admin_orders_requires_correct_pin(client):
    await client.post(
        "/api/orders",
        json={"customer_name": "A", "customer_phone": "1", "raw_text": "x"},
    )
    assert (await client.get("/api/admin/orders")).status_code == 401
    assert (
        await client.get("/api/admin/orders", headers={"X-Admin-Pin": "nope"})
    ).status_code == 401
    ok = await client.get("/api/admin/orders", headers=ADMIN_HEADERS)
    assert ok.status_code == 200
    assert len(ok.json()) == 1


async def test_correction_never_overwrites_raw_text(client):
    created = (
        await client.post(
            "/api/orders",
            json={"customer_name": "A", "customer_phone": "1", "raw_text": "the original words"},
        )
    ).json()
    res = await client.patch(
        f"/api/admin/orders/{created['id']}",
        headers=ADMIN_HEADERS,
        json={
            "structured_items": [
                {"name": "Veg Thali", "quantity": 1, "matched": True, "unit_price_cents": 1000}
            ],
            "correction_note": "fixed by Dad",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["raw_text"] == "the original words"  # never changed
    assert body["status"] == "parsed"
    assert body["corrected_at"] is not None
    assert body["correction_note"] == "fixed by Dad"
    assert body["total_cents"] == 1000
