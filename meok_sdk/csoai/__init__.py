"""CSOAI module — programmatic access to csoai.org data."""

from .client import AsyncCSOAIClient, CSOAIClient
from .errors import (
    CSOAIAPIError,
    CSOAIAuthError,
    CSOAIError,
    CSOAINetworkError,
    CSOAIRateLimitError,
    CSOAIServerError,
)
from .models import (
    ComplianceMap,
    CouncilVote,
    CrosswalkRow,
    DOMEStatus,
    Framework,
    Region,
    RegulatoryCountdown,
    SigilVerification,
)

__all__ = [
    # Clients
    "CSOAIClient",
    "AsyncCSOAIClient",
    # Models
    "ComplianceMap",
    "Region",
    "Framework",
    "CrosswalkRow",
    "DOMEStatus",
    "CouncilVote",
    "SigilVerification",
    "RegulatoryCountdown",
    # Errors
    "CSOAIError",
    "CSOAIAPIError",
    "CSOAIAuthError",
    "CSOAINetworkError",
    "CSOAIRateLimitError",
    "CSOAIServerError",
]
