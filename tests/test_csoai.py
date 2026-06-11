"""CSOAI client tests — uses respx to intercept httpx requests."""

from __future__ import annotations

import httpx
import pytest
import respx

from meok_sdk.csoai import (
    AsyncCSOAIClient,
    CSOAIClient,
    CSOAIAPIError,
    CSOAINetworkError,
    CSOAIAuthError,
    ComplianceMap,
    CouncilVote,
    CrosswalkRow,
    DOMEStatus,
    Region,
    RegulatoryCountdown,
    SigilVerification,
)

BASE = "https://csoai.org"


@pytest.fixture
def mocked_router() -> respx.MockRouter:
    with respx.mock(base_url=BASE) as router:
        yield router


# ── Compliance Map ───────────────────────────────────────────────────


def test_get_compliance_map(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/map.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "regions": [
                    {"code": "eu", "name": "European Union", "frameworks": ["EU_AI_ACT"], "active": True}
                ],
                "frameworks": [
                    {"id": "EU_AI_ACT", "name": "EU AI Act", "region": "eu", "status": "active"}
                ],
                "generated_at": "2026-06-11T12:00:00Z",
            },
        )
    )
    with CSOAIClient() as c:
        result = c.get_compliance_map()
    assert isinstance(result, ComplianceMap)
    assert len(result.regions) == 1
    assert result.regions[0].code == "eu"
    assert result.frameworks[0].id == "EU_AI_ACT"
    assert result.generated_at == "2026-06-11T12:00:00Z"


# ── Crosswalk ────────────────────────────────────────────────────────


def test_get_crosswalk(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/crosswalk.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "rows": [
                    {
                        "source_framework": "EU_AI_ACT",
                        "target_framework": "UK_AI_BILL",
                        "mapping_type": "direct",
                        "confidence": 0.92,
                        "articles": ["Art 5", "Art 6"],
                        "notes": "High alignment",
                    }
                ]
            },
        )
    )
    with CSOAIClient() as c:
        result = c.get_crosswalk()
    assert len(result) == 1
    assert isinstance(result[0], CrosswalkRow)
    assert result[0].source_framework == "EU_AI_ACT"
    assert result[0].confidence == 0.92


def test_get_crosswalk_plain_list(mocked_router: respx.MockRouter) -> None:
    """API may return a plain list instead of a wrapped object."""
    mocked_router.get("/api/crosswalk.json").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "source_framework": "GDPR",
                    "target_framework": "CCPA",
                    "mapping_type": "partial",
                    "confidence": 0.75,
                }
            ],
        )
    )
    with CSOAIClient() as c:
        result = c.get_crosswalk()
    assert len(result) == 1
    assert result[0].target_framework == "CCPA"


# ── DOME Status ──────────────────────────────────────────────────────


def test_get_dome_status(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/dome/status.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "healthy",
                "last_updated": "2026-06-11T11:00:00Z",
                "regions_online": 5,
                "frameworks_tracked": 12,
                "alerts_active": 2,
            },
        )
    )
    with CSOAIClient() as c:
        result = c.get_dome_status()
    assert isinstance(result, DOMEStatus)
    assert result.status == "healthy"
    assert result.regions_online == 5
    assert result.alerts_active == 2


# ── Council Votes ────────────────────────────────────────────────────


def test_get_council_votes(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/council/votes.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "votes": [
                    {
                        "vote_id": "V-2026-001",
                        "topic": "AI Act Annex III expansion",
                        "region": "eu",
                        "outcome": "passed",
                        "date": "2026-05-20",
                        "ayes": 42,
                        "nays": 3,
                        "abstentions": 5,
                    }
                ]
            },
        )
    )
    with CSOAIClient() as c:
        result = c.get_council_votes()
    assert len(result) == 1
    assert isinstance(result[0], CouncilVote)
    assert result[0].vote_id == "V-2026-001"
    assert result[0].ayes == 42


# ── Sigil Verification ───────────────────────────────────────────────


def test_verify_sigil(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/sigil/verify.json?id=WD-2026-001").mock(
        return_value=httpx.Response(
            200,
            json={
                "valid": True,
                "sigil_id": "WD-2026-001",
                "entity": "ACME Haulage Ltd",
                "regulation": "EU_AI_ACT",
                "issued_at": "2026-01-15T09:00:00Z",
                "expires_at": "2027-01-15T09:00:00Z",
                "message": "Sigil is valid and active.",
            },
        )
    )
    with CSOAIClient() as c:
        result = c.verify_sigil("WD-2026-001")
    assert isinstance(result, SigilVerification)
    assert result.valid is True
    assert result.sigil_id == "WD-2026-001"
    assert result.entity == "ACME Haulage Ltd"


# ── Region Lookup ────────────────────────────────────────────────────


def test_get_region(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/map.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "regions": [
                    {"code": "eu", "name": "European Union", "frameworks": ["EU_AI_ACT"]},
                    {"code": "uk", "name": "United Kingdom", "frameworks": ["UK_AI_BILL"]},
                ],
                "frameworks": [],
            },
        )
    )
    with CSOAIClient() as c:
        region = c.get_region("eu")
    assert isinstance(region, Region)
    assert region.code == "eu"
    assert region.name == "European Union"


def test_get_region_not_found(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/map.json").mock(
        return_value=httpx.Response(200, json={"regions": [], "frameworks": []})
    )
    with CSOAIClient() as c:
        region = c.get_region("xx")
    assert region is None


# ── Regulatory Countdowns ────────────────────────────────────────────


def test_get_regulatory_countdowns(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/countdowns.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "countdowns": [
                    {
                        "framework_id": "EU_AI_ACT",
                        "framework_name": "EU AI Act",
                        "region": "eu",
                        "deadline": "2026-08-02",
                        "days_remaining": 52,
                        "urgency": "high",
                    }
                ]
            },
        )
    )
    with CSOAIClient() as c:
        result = c.get_regulatory_countdowns()
    assert len(result) == 1
    assert isinstance(result[0], RegulatoryCountdown)
    assert result[0].framework_id == "EU_AI_ACT"
    assert result[0].days_remaining == 52


# ── Errors ───────────────────────────────────────────────────────────


def test_network_error(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/map.json").mock(side_effect=httpx.ConnectError("DNS fail"))
    with CSOAIClient() as c:
        with pytest.raises(CSOAINetworkError):
            c.get_compliance_map()


def test_api_error_401(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/map.json").mock(
        return_value=httpx.Response(401, json={"error": "Unauthorized"})
    )
    with CSOAIClient(api_key="bad_key") as c:
        with pytest.raises(CSOAIAuthError) as excinfo:
            c.get_compliance_map()
        assert excinfo.value.status_code == 401


def test_api_error_500(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/map.json").mock(
        return_value=httpx.Response(500, json={"error": "Internal Server Error"})
    )
    with CSOAIClient() as c:
        with pytest.raises(CSOAIAPIError) as excinfo:
            c.get_compliance_map()
        assert excinfo.value.status_code == 500


# ── Async ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_async_get_compliance_map(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/map.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "regions": [{"code": "us", "name": "United States", "frameworks": ["NIST_AI_RMF"]}],
                "frameworks": [],
            },
        )
    )
    async with AsyncCSOAIClient() as c:
        result = await c.get_compliance_map()
    assert isinstance(result, ComplianceMap)
    assert result.regions[0].code == "us"


@pytest.mark.asyncio
async def test_async_get_region(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/map.json").mock(
        return_value=httpx.Response(
            200,
            json={
                "regions": [
                    {"code": "cn", "name": "China", "frameworks": ["TC260"]},
                ],
                "frameworks": [],
            },
        )
    )
    async with AsyncCSOAIClient() as c:
        region = await c.get_region("cn")
    assert isinstance(region, Region)
    assert region.code == "cn"


@pytest.mark.asyncio
async def test_async_network_error(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/api/dome/status.json").mock(side_effect=httpx.ConnectError("DNS fail"))
    async with AsyncCSOAIClient() as c:
        with pytest.raises(CSOAINetworkError):
            await c.get_dome_status()
