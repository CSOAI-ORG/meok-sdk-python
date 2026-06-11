"""Exception hierarchy for the CSOAI module."""

from __future__ import annotations

from meok_sdk.errors import MeokError


class CSOAIError(MeokError):
    """Base for every error raised by the CSOAI client."""


class CSOAINetworkError(CSOAIError):
    """Connection / DNS / TLS / timeout — the request never reached csoai.org."""


class CSOAIAPIError(CSOAIError):
    """The API responded with a non-2xx status."""

    def __init__(self, status_code: int, message: str, *, body: object = None) -> None:
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.message = message
        self.body = body


class CSOAIAuthError(CSOAIAPIError):
    """401 — missing/invalid API key."""


class CSOAIRateLimitError(CSOAIAPIError):
    """429 — too many requests."""


class CSOAIServerError(CSOAIAPIError):
    """5xx — upstream server error."""


def from_response(status_code: int, body: object) -> CSOAIAPIError:
    """Pick the right CSOAIAPIError subclass from an HTTP status code."""
    message = ""
    if isinstance(body, dict):
        message = str(body.get("error") or body.get("message") or "")
    if not message:
        message = "(no error message in response body)"

    if status_code == 401:
        return CSOAIAuthError(status_code, message, body=body)
    if status_code == 429:
        return CSOAIRateLimitError(status_code, message, body=body)
    if status_code >= 500:
        return CSOAIServerError(status_code, message, body=body)
    return CSOAIAPIError(status_code, message, body=body)
