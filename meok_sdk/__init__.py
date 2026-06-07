"""
MEOK Python SDK — sign + verify HMAC-signed compliance attestations.

Quick start
-----------

    from meok_sdk import MeokClient

    client = MeokClient(api_key="sk_meok_…")
    cert = client.sign(
        regulation="EU_AI_ACT_ANNEX_III",
        entity="ACME Haulage Ltd",
        score=82,
        findings=["Tachograph data exported", "OCRS forecast GREEN"],
    )

    # …and from anywhere — no key needed for verification:
    is_valid = MeokClient.verify_public(cert)

Async variant: :class:`AsyncMeokClient` mirrors the sync surface with `await`.
"""

from .client import AsyncMeokClient, MeokClient
from .errors import (
    MeokAPIError,
    MeokAuthError,
    MeokError,
    MeokNetworkError,
    MeokValidationError,
)
from .models import Assessment, Cert, Tier, VerifyResult

__version__ = "0.1.1"
__all__ = [
    # Clients
    "MeokClient",
    "AsyncMeokClient",
    # Models
    "Cert",
    "VerifyResult",
    "Assessment",
    "Tier",
    # Errors
    "MeokError",
    "MeokAPIError",
    "MeokAuthError",
    "MeokNetworkError",
    "MeokValidationError",
]
