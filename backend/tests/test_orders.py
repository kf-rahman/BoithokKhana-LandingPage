"""Acceptance tests for order submission (docs/stories/order-submission.md)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.order import Order

VALID_PAYLOAD = {
    "customer_name": "Asha",
    "customer_email": "asha@example.com",
    "customer_phone": "+1 416 555 0199",
    "raw_text": "2 chicken biryani no spice, 1 veg thali, deliver Friday",
}


def test_submit_order_persists_raw_text_first(
    client: TestClient, db_session: Session
) -> None:
    res = client.post("/api/orders", json=VALID_PAYLOAD)

    assert res.status_code == 201
    body = res.json()
    assert body["id"] > 0
    assert body["raw_text"] == VALID_PAYLOAD["raw_text"]
    assert body["customer_email"] == VALID_PAYLOAD["customer_email"]
    assert body["status"] == "pending_parse"
    assert body["items"] == []  # no structured line items until parsing runs
    assert body["confirmation_email_sent"] is False
    assert body["delivered"] is False

    # Actually persisted, with the raw text intact.
    row = db_session.get(Order, body["id"])
    assert row is not None
    assert row.raw_text == VALID_PAYLOAD["raw_text"]
    assert row.status == "pending_parse"


def test_raw_text_is_stored_verbatim(
    client: TestClient, db_session: Session
) -> None:
    raw = "  2 biryani\n  no onions  \U0001f336 "
    res = client.post("/api/orders", json={**VALID_PAYLOAD, "raw_text": raw})
    assert res.status_code == 201
    # Not trimmed, not normalized — exactly what the customer typed.
    assert res.json()["raw_text"] == raw
    # And the persisted row matches byte-for-byte (defense-in-depth on the
    # project's #1 non-negotiable: raw text is never altered).
    row = db_session.get(Order, res.json()["id"])
    assert row is not None
    assert row.raw_text == raw


def test_empty_order_is_rejected_and_nothing_saved(
    client: TestClient, db_session: Session
) -> None:
    res = client.post("/api/orders", json={**VALID_PAYLOAD, "raw_text": "   "})
    assert res.status_code == 422
    assert db_session.query(Order).count() == 0


def test_invalid_email_is_rejected(client: TestClient) -> None:
    res = client.post(
        "/api/orders", json={**VALID_PAYLOAD, "customer_email": "not-an-email"}
    )
    assert res.status_code == 422


def test_missing_required_fields_rejected(client: TestClient) -> None:
    res = client.post("/api/orders", json={"customer_name": "Sam"})
    assert res.status_code == 422


def test_confirmation_email_sent_when_smtp_configured(client: TestClient, monkeypatch) -> None:
    from app.config import settings
    from app.services import email

    sent: dict[str, str] = {}

    def fake_send(to: str, subject: str, body: str) -> None:
        sent["to"] = to

    monkeypatch.setattr(settings, "smtp_host", "smtp.test")
    monkeypatch.setattr(email, "_send_email", fake_send)

    res = client.post("/api/orders", json=VALID_PAYLOAD)
    assert res.status_code == 201
    assert res.json()["confirmation_email_sent"] is True
    assert sent["to"] == VALID_PAYLOAD["customer_email"]
