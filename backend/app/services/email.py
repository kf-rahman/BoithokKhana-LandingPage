"""Customer order-confirmation email.

Generic SMTP so it works with any provider (SES, SendGrid, Mailgun, ...). It is
a no-op when SMTP isn't configured, and a delivery failure never raises — a
flaky mail server must not break order submission. The single send function is
isolated so it can be mocked in tests.
"""

import smtplib
from email.message import EmailMessage

from app.config import settings
from app.models.order import Order


def _send_email(to: str, subject: str, body: str) -> None:
    """Send one email via SMTP. Isolated for mocking."""
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)


def send_order_confirmation(order: Order) -> bool:
    """Email the customer a receipt confirmation.

    Returns True if an email was sent, False if email is disabled (no SMTP host)
    or there's no recipient. Never raises — delivery is best-effort.
    """
    if not settings.smtp_host or not order.customer_email:
        return False

    subject = "We received your order — Boithok Khana"
    body = (
        f"Hi {order.customer_name},\n\n"
        "Thanks for your order! We've received it and will confirm the details "
        "with you shortly.\n\n"
        "Your order, as you sent it:\n"
        f"{order.raw_text}\n\n"
        "— Boithok Khana"
    )
    try:
        _send_email(order.customer_email, subject, body)
        return True
    except Exception:  # noqa: BLE001 — delivery must never break submission
        return False
