"""Exception hierarchy for the MEOK SDK.

All exceptions inherit from :class:`MeokError` so callers can catch broadly
or narrowly as appropriate.
"""

from __future__ import annotations


class MeokError(Exception):
    """Base for every error raised by the SDK."""


class MeokNetworkError(MeokError):
    """Connection / DNS / TLS / timeout — the request never reached MEOK."""


class MeokAPIError(MeokError):
    """The API responded with a non-2xx status."""

    def __init__(self, status_code: int, message: str, *, body: object = None) -> None:
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.message = message
        self.body = body


class MeokAuthError(MeokAPIError):
    """401 — missing/invalid API key."""


class MeokValidationError(MeokAPIError):
    """400 — missing required fields, wrong type, etc."""


class MeokPaymentError(MeokAPIError):
    """402 — Stripe session not paid / not complete (for /provision)."""


def from_response(status_code: int, body: object) -> MeokAPIError:
    """Pick the right MeokAPIError subclass from an HTTP status code."""
    message = ""
    if isinstance(body, dict):
        message = str(body.get("error") or body.get("message") or "")
    if not message:
        message = "(no error message in response body)"

    if status_code == 401:
        return MeokAuthError(status_code, message, body=body)
    if status_code == 400:
        return MeokValidationError(status_code, message, body=body)
    if status_code == 402:
        return MeokPaymentError(status_code, message, body=body)
    return MeokAPIError(status_code, message, body=body)
