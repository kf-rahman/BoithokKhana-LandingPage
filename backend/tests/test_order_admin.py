"""Tests for the admin orders endpoints (list + fulfillment flags)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.order import Order

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

    # Partial update leaves the unspecified flag unchanged.
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
