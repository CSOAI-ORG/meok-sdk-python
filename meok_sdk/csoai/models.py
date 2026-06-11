"""Typed models for the CSOAI public API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Region:
    """A regulatory region (e.g. EU, UK, US, CN)."""

    code: str
    name: str
    frameworks: list[str] = field(default_factory=list)
    active: bool = True

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "Region":
        return cls(
            code=str(body.get("code", "")),
            name=str(body.get("name", "")),
            frameworks=list(body.get("frameworks", [])),
            active=bool(body.get("active", True)),
        )


@dataclass(frozen=True)
class Framework:
    """A compliance framework within a region."""

    id: str
    name: str
    region: str
    status: str
    effective_date: str | None = None
    url: str | None = None

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "Framework":
        return cls(
            id=str(body.get("id", "")),
            name=str(body.get("name", "")),
            region=str(body.get("region", "")),
            status=str(body.get("status", "")),
            effective_date=(str(body["effective_date"]) if body.get("effective_date") else None),
            url=(str(body["url"]) if body.get("url") else None),
        )


@dataclass(frozen=True)
class CrosswalkRow:
    """One row of the crosswalk mapping frameworks across regions."""

    source_framework: str
    target_framework: str
    mapping_type: str
    confidence: float
    articles: list[str] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "CrosswalkRow":
        return cls(
            source_framework=str(body.get("source_framework", "")),
            target_framework=str(body.get("target_framework", "")),
            mapping_type=str(body.get("mapping_type", "")),
            confidence=float(body.get("confidence", 0.0)),
            articles=list(body.get("articles", [])),
            notes=str(body.get("notes", "")),
        )


@dataclass(frozen=True)
class DOMEStatus:
    """Status of the DOME (Data Observatory & Monitoring Engine)."""

    status: str
    last_updated: str | None = None
    regions_online: int = 0
    frameworks_tracked: int = 0
    alerts_active: int = 0

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "DOMEStatus":
        return cls(
            status=str(body.get("status", "")),
            last_updated=(str(body["last_updated"]) if body.get("last_updated") else None),
            regions_online=int(body.get("regions_online", 0)),
            frameworks_tracked=int(body.get("frameworks_tracked", 0)),
            alerts_active=int(body.get("alerts_active", 0)),
        )


@dataclass(frozen=True)
class CouncilVote:
    """A single council vote record."""

    vote_id: str
    topic: str
    region: str
    outcome: str
    date: str | None = None
    ayes: int = 0
    nays: int = 0
    abstentions: int = 0

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "CouncilVote":
        return cls(
            vote_id=str(body.get("vote_id", "")),
            topic=str(body.get("topic", "")),
            region=str(body.get("region", "")),
            outcome=str(body.get("outcome", "")),
            date=(str(body["date"]) if body.get("date") else None),
            ayes=int(body.get("ayes", 0)),
            nays=int(body.get("nays", 0)),
            abstentions=int(body.get("abstentions", 0)),
        )


@dataclass(frozen=True)
class SigilVerification:
    """Result of verifying a sigil / certification identifier."""

    valid: bool
    sigil_id: str
    entity: str | None = None
    regulation: str | None = None
    issued_at: str | None = None
    expires_at: str | None = None
    message: str = ""

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "SigilVerification":
        return cls(
            valid=bool(body.get("valid", False)),
            sigil_id=str(body.get("sigil_id", "")),
            entity=(str(body["entity"]) if body.get("entity") else None),
            regulation=(str(body["regulation"]) if body.get("regulation") else None),
            issued_at=(str(body["issued_at"]) if body.get("issued_at") else None),
            expires_at=(str(body["expires_at"]) if body.get("expires_at") else None),
            message=str(body.get("message", "")),
        )


@dataclass(frozen=True)
class RegulatoryCountdown:
    """A countdown to a regulatory deadline."""

    framework_id: str
    framework_name: str
    region: str
    deadline: str
    days_remaining: int
    urgency: str

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "RegulatoryCountdown":
        return cls(
            framework_id=str(body.get("framework_id", "")),
            framework_name=str(body.get("framework_name", "")),
            region=str(body.get("region", "")),
            deadline=str(body.get("deadline", "")),
            days_remaining=int(body.get("days_remaining", 0)),
            urgency=str(body.get("urgency", "")),
        )


@dataclass(frozen=True)
class ComplianceMap:
    """Top-level response from ``/api/map.json``."""

    regions: list[Region] = field(default_factory=list)
    frameworks: list[Framework] = field(default_factory=list)
    generated_at: str | None = None

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "ComplianceMap":
        return cls(
            regions=[Region.from_json(r) for r in body.get("regions", [])],
            frameworks=[Framework.from_json(f) for f in body.get("frameworks", [])],
            generated_at=(str(body["generated_at"]) if body.get("generated_at") else None),
        )
