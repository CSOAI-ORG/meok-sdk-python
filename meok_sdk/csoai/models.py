"""Typed models for the CSOAI public API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Region:
    """A regulatory region (e.g. EU, UK, US, CN)."""

    id: str
    name: str
    status: str
    status_label: str
    color: str
    days_to_deadline: int = 0
    deadline_date: str | None = None
    frameworks: list[str] = field(default_factory=list)
    agents: int = 0
    compliance_score: int = 0
    open_violations: int = 0

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "Region":
        return cls(
            id=str(body.get("id", "")),
            name=str(body.get("name", "")),
            status=str(body.get("status", "")),
            status_label=str(body.get("status_label", "")),
            color=str(body.get("color", "")),
            days_to_deadline=int(body.get("days_to_deadline", 0)),
            deadline_date=(str(body["deadline_date"]) if body.get("deadline_date") else None),
            frameworks=list(body.get("frameworks", [])),
            agents=int(body.get("agents", 0)),
            compliance_score=int(body.get("compliance_score", 0)),
            open_violations=int(body.get("open_violations", 0)),
        )


@dataclass(frozen=True)
class Framework:
    """A compliance framework within a region."""

    id: str
    name: str
    region: str
    status: str
    effective_date: str | None = None

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "Framework":
        return cls(
            id=str(body.get("id", "")),
            name=str(body.get("name", "")),
            region=str(body.get("region", "")),
            status=str(body.get("status", "")),
            effective_date=(str(body["effective_date"]) if body.get("effective_date") else None),
        )


@dataclass(frozen=True)
class CrosswalkRow:
    """One row of the crosswalk mapping frameworks across regions."""

    domain: str
    eu_ai_act: str
    nist_ai_rmf: str
    iso_42001: str
    tc260: str
    risk: str

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "CrosswalkRow":
        return cls(
            domain=str(body.get("domain", "")),
            eu_ai_act=str(body.get("eu_ai_act", "")),
            nist_ai_rmf=str(body.get("nist_ai_rmf", "")),
            iso_42001=str(body.get("iso_42001", "")),
            tc260=str(body.get("tc260", "")),
            risk=str(body.get("risk", "")),
        )


@dataclass(frozen=True)
class DOMEStatus:
    """Status of the DOME (Data Observatory & Monitoring Engine)."""

    version: str
    generated_at: str
    status: str
    layer: str
    active_systems: int = 0
    pdca_cycles: int = 0
    mcp_servers: int = 0
    open_violations: int = 0
    avg_compliance: int = 0
    pending_approvals: int = 0

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "DOMEStatus":
        stats = body.get("stats", {})
        return cls(
            version=str(body.get("version", "")),
            generated_at=str(body.get("generated_at", "")),
            status=str(body.get("status", "")),
            layer=str(body.get("layer", "")),
            active_systems=int(stats.get("active_systems", 0)),
            pdca_cycles=int(stats.get("pdca_cycles", 0)),
            mcp_servers=int(stats.get("mcp_servers", 0)),
            open_violations=int(stats.get("open_violations", 0)),
            avg_compliance=int(stats.get("avg_compliance", 0)),
            pending_approvals=int(stats.get("pending_approvals", 0)),
        )


@dataclass(frozen=True)
class CouncilVote:
    """A single council vote record."""

    topic: str
    result: str
    count: str
    time: str
    proposal_id: str

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "CouncilVote":
        return cls(
            topic=str(body.get("topic", "")),
            result=str(body.get("result", "")),
            count=str(body.get("count", "")),
            time=str(body.get("time", "")),
            proposal_id=str(body.get("proposal_id", "")),
        )


@dataclass(frozen=True)
class SigilVerification:
    """Result of verifying a sigil / certification identifier."""

    valid: bool
    cert_id: str
    system_name: str = ""
    framework: str = ""
    compliance_score: float = 0.0
    issued_at: str | None = None
    expires_at: str | None = None
    issuer: str = ""
    status: str = ""

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "SigilVerification":
        return cls(
            valid=bool(body.get("valid", False)),
            cert_id=str(body.get("cert_id", "")),
            system_name=str(body.get("system_name", "")),
            framework=str(body.get("framework", "")),
            compliance_score=float(body.get("compliance_score", 0.0)),
            issued_at=(str(body["issued_at"]) if body.get("issued_at") else None),
            expires_at=(str(body["expires_at"]) if body.get("expires_at") else None),
            issuer=str(body.get("issuer", "")),
            status=str(body.get("status", "")),
        )


@dataclass(frozen=True)
class RegulatoryCountdown:
    """A countdown to a regulatory deadline."""

    name: str
    days_remaining: int
    deadline: str
    color: str

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "RegulatoryCountdown":
        return cls(
            name=str(body.get("name", "")),
            days_remaining=int(body.get("days_remaining", 0)),
            deadline=str(body.get("deadline", "")),
            color=str(body.get("color", "")),
        )


@dataclass(frozen=True)
class ComplianceMap:
    """Top-level response from ``/api/map.json``."""

    version: str
    generated_at: str
    total_regions: int
    total_frameworks: int
    regions: list[Region] = field(default_factory=list)
    global_stats: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "ComplianceMap":
        return cls(
            version=str(body.get("version", "")),
            generated_at=str(body.get("generated_at", "")),
            total_regions=int(body.get("total_regions", 0)),
            total_frameworks=int(body.get("total_frameworks", 0)),
            regions=[Region.from_json(r) for r in body.get("regions", [])],
            global_stats=body.get("global_stats", {}),
        )


@dataclass(frozen=True)
class Crosswalk:
    """Top-level response from ``/api/crosswalk.json``."""

    version: str
    generated_at: str
    total_frameworks: int
    total_domains: int
    frameworks: list[Framework] = field(default_factory=list)
    crosswalk: list[CrosswalkRow] = field(default_factory=list)

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "Crosswalk":
        return cls(
            version=str(body.get("version", "")),
            generated_at=str(body.get("generated_at", "")),
            total_frameworks=int(body.get("total_frameworks", 0)),
            total_domains=int(body.get("total_domains", 0)),
            frameworks=[Framework.from_json(f) for f in body.get("frameworks", [])],
            crosswalk=[CrosswalkRow.from_json(r) for r in body.get("crosswalk", [])],
        )


@dataclass(frozen=True)
class CouncilVotes:
    """Top-level response from ``/api/council/votes.json``."""

    version: str
    generated_at: str
    council: dict[str, Any] = field(default_factory=dict)
    nodes: list[dict[str, Any]] = field(default_factory=list)
    recent_votes: list[CouncilVote] = field(default_factory=list)
    vote_counts: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_json(cls, body: dict[str, Any]) -> "CouncilVotes":
        return cls(
            version=str(body.get("version", "")),
            generated_at=str(body.get("generated_at", "")),
            council=body.get("council", {}),
            nodes=body.get("nodes", []),
            recent_votes=[CouncilVote.from_json(v) for v in body.get("recent_votes", [])],
            vote_counts=body.get("vote_counts", {}),
        )

