"""Error reporting (Sentry).

Disabled by default. Nothing leaves this server until `SENTRY_DSN` is set, so
this module is safe to ship before the Sentry account exists.

Privacy note: customers type their orders as free text, which routinely
contains names, phone numbers, addresses and delivery instructions. That text
is the one thing this project promises never to lose or mishandle, so we do
not ship it to a third party to debug a crash. `send_default_pii=False` keeps
request bodies, headers and cookies out of events, and `_scrub` strips the
order fields that could still ride along inside local variables.
"""

from __future__ import annotations

from typing import Any

from app.config import settings

# Local variables with these names are redacted before an event is sent. They
# are the fields that carry customer-identifying text through the parser and
# the order routes.
_SENSITIVE_KEYS = frozenset(
    {
        "raw_text",
        "customer_name",
        "customer_email",
        "customer_phone",
        "delivery_notes",
        "unmatched_text",
        "admin_pin",
        "x_admin_pin",
        "anthropic_api_key",
        "smtp_password",
    }
)

_REDACTED = "[redacted]"


def _scrub(event: dict[str, Any], _hint: dict[str, Any]) -> dict[str, Any]:
    """Redact customer text and secrets from stack-frame local variables."""
    for exception in event.get("exception", {}).get("values", []):
        for frame in exception.get("stacktrace", {}).get("frames", []):
            variables = frame.get("vars")
            if not isinstance(variables, dict):
                continue
            for name in list(variables):
                if name.lower() in _SENSITIVE_KEYS:
                    variables[name] = _REDACTED
    # Belt and braces: the request body should already be absent with
    # send_default_pii=False, but an order body is exactly what we must never
    # leak, so drop it unconditionally.
    request = event.get("request")
    if isinstance(request, dict):
        request.pop("data", None)
        request.pop("cookies", None)
    return event


def init_error_reporting() -> bool:
    """Start Sentry if a DSN is configured.

    Returns True if reporting is active, False if it's switched off. Never
    raises: a misconfigured error reporter must not stop Dad taking orders.
    """
    if not settings.sentry_dsn:
        return False

    try:
        import sentry_sdk
    except ImportError:
        # The dependency is in requirements.txt, but an incomplete install
        # should degrade to "no error reporting", not a dead API.
        return False

    try:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            send_default_pii=False,
            before_send=_scrub,
        )
    except Exception:  # noqa: BLE001 — reporting must never break the app.
        return False
    return True
