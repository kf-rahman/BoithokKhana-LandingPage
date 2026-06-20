"""Tests for menu publishing (admin) and the public current-menu endpoint."""

from datetime import date

from fastapi.testclient import TestClient

PIN = {"X-Admin-Pin": "1234"}


def _menu_payload() -> dict:
    return {
        "week_of": str(date(2026, 6, 22)),
        "items": [
            {"name": "Chicken Biryani", "price_cents": 1500},
            {"name": "Veg Thali", "price_cents": 1200},
        ],
    }


def test_create_menu_requires_pin(client: TestClient) -> None:
    res = client.post("/api/admin/menus", json=_menu_payload())
    assert res.status_code == 401


def test_wrong_pin_rejected(client: TestClient) -> None:
    res = client.post(
        "/api/admin/menus", json=_menu_payload(), headers={"X-Admin-Pin": "0000"}
    )
    assert res.status_code == 401


def test_create_then_publish_then_current(client: TestClient) -> None:
    # Create a draft menu.
    res = client.post("/api/admin/menus", json=_menu_payload(), headers=PIN)
    assert res.status_code == 201
    menu = res.json()
    assert menu["status"] == "draft"
    assert len(menu["items"]) == 2
    assert menu["items"][0]["price_cents"] == 1500
    menu_id = menu["id"]

    # Nothing published yet → no current menu.
    assert client.get("/api/menus/current").status_code == 404

    # Publish it.
    pub = client.post(f"/api/admin/menus/{menu_id}/publish", headers=PIN)
    assert pub.status_code == 200
    assert pub.json()["status"] == "published"
    assert pub.json()["published_at"] is not None

    # Now it is the current menu (public, no PIN needed).
    cur = client.get("/api/menus/current")
    assert cur.status_code == 200
    assert cur.json()["id"] == menu_id
    assert {i["name"] for i in cur.json()["items"]} == {"Chicken Biryani", "Veg Thali"}


def test_publish_missing_menu_404(client: TestClient) -> None:
    assert client.post("/api/admin/menus/999/publish", headers=PIN).status_code == 404


def test_create_menu_requires_at_least_one_item(client: TestClient) -> None:
    res = client.post(
        "/api/admin/menus",
        json={"week_of": str(date(2026, 6, 22)), "items": []},
        headers=PIN,
    )
    assert res.status_code == 422
