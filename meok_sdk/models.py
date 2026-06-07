"""Typed models matching the MEOK Attestation API OpenAPI 3.1 schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict

# ── Literal types — narrow validation surface ────────────────────────────
Assessment = Literal[
    "COMPLIANT",
    "PARTIAL",
    "NON_COMPLIANT",
    "COMPLIANT (UNVERIFIED — free tier)",
    "PARTIAL (UNVERIFIED — free tier)",
    "NON_COMPLIANT (UNVERIFIED — free tier)",
]

Tier = Literal["free", "starter", "pro", "enterprise"]


class Cert(TypedDict, total=False):
    """Shape of a signed attestation returned by `/sign` and accepted by `/verify`.

    All fields are optional because the API ships forward-compatible additions
    on the cert envelope. Use ``cert.get("…")`` for safe access.
    """

    cert_id: str
    issued_at: str  # ISO-8601 UTC
    expires_at: str  # ISO-8601 UTC, ~1y after issued_at
    regulation: str
    entity: str
    score: float
    assessment: Assessment
    findings: list[str]
    articles_audited: list[str]
    auditor_notes: str
    tier: Tier
    issuer: str
    kid: str
    verify_url: str
    signature_sha256_hmac: str


@dataclass(frozen=True)
class VerifyResult:
    """Outcome of a public verification call."""

    valid: bool
    message: str
    cert_id: str | None = None
    verify_url: str | None = None

    @classmethod
    def from_json(cls, body: dict[str, object]) -> "VerifyResult":
        return cls(
            valid=bool(body.get("valid", False)),
            message=str(body.get("message", "")),
            cert_id=(str(body["cert_id"]) if body.get("cert_id") else None),
            verify_url=(str(body["verify_url"]) if body.get("verify_url") else None),
        )


@dataclass
class SignRequest:
    """Convenience builder for the body of `POST /sign`."""

    regulation: str
    entity: str
    score: float
    findings: list[str] = field(default_factory=list)
    articles_audited: list[str] = field(default_factory=list)
    auditor_notes: str = ""

    def to_json(self) -> dict[str, object]:
        body: dict[str, object] = {
            "regulation": self.regulation,
            "entity": self.entity,
            "score": float(self.score),
        }
        if self.findings:
            body["findings"] = list(self.findings)
        if self.articles_audited:
            body["articles_audited"] = list(self.articles_audited)
        if self.auditor_notes:
            body["auditor_notes"] = self.auditor_notes
        return body
