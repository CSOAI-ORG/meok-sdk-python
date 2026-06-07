"""Sync MeokClient tests — uses respx to intercept httpx requests."""

from __future__ import annotations

import httpx
import pytest
import respx

from meok_sdk import (
    AsyncMeokClient,
    MeokAuthError,
    MeokClient,
    MeokNetworkError,
    MeokValidationError,
    VerifyResult,
)

BASE = "https://meok-attestation-api.vercel.app"


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def mocked_router() -> respx.MockRouter:
    with respx.mock(base_url=BASE) as router:
        yield router


# ── Health ───────────────────────────────────────────────────────────


def test_health_ok(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/health").mock(
        return_value=httpx.Response(200, json={"ok": True, "status": "ok"})
    )
    with MeokClient(api_key="sk_test") as c:
        result = c.health()
        assert result["ok"] is True


def test_health_network_error(mocked_router: respx.MockRouter) -> None:
    mocked_router.get("/health").mock(side_effect=httpx.ConnectError("DNS fail"))
    with MeokClient(api_key="sk_test") as c:
        with pytest.raises(MeokNetworkError):
            c.health()


# ── Sign ─────────────────────────────────────────────────────────────


def test_sign_without_api_key_raises() -> None:
    with MeokClient(api_key=None) as c:
        # Force-clear in case env var is set
        c.api_key = None
        with pytest.raises(MeokAuthError):
            c.sign(regulation="GDPR", entity="ACME", score=80)


def test_sign_returns_cert(mocked_router: respx.MockRouter) -> None:
    fake_cert = {
        "cert_id": "abc123",
        "regulation": "GDPR",
        "entity": "ACME",
        "score": 80.0,
        "assessment": "COMPLIANT",
        "signature_sha256_hmac": "deadbeef",
        "issuer": "meok-attestation-api",
        "kid": "v1",
        "verify_url": f"{BASE}/v/abc123",
    }
    route = mocked_router.post("/sign").mock(return_value=httpx.Response(200, json=fake_cert))
    with MeokClient(api_key="sk_test") as c:
        cert = c.sign(regulation="GDPR", entity="ACME", score=80, findings=["X", "Y"])
        assert cert["cert_id"] == "abc123"
        assert cert["assessment"] == "COMPLIANT"

    # Verify body shape
    payload = route.calls.last.request.read().decode("utf-8")
    assert "GDPR" in payload
    assert "ACME" in payload
    assert "sk_test" in payload


def test_sign_400_raises_validation(mocked_router: respx.MockRouter) -> None:
    mocked_router.post("/sign").mock(
        return_value=httpx.Response(400, json={"error": "'regulation' required"})
    )
    with MeokClient(api_key="sk_test") as c:
        with pytest.raises(MeokValidationError) as excinfo:
            c.sign(regulation="", entity="ACME", score=80)
        assert excinfo.value.status_code == 400


# ── Verify ───────────────────────────────────────────────────────────


def test_verify_returns_result(mocked_router: respx.MockRouter) -> None:
    mocked_router.post("/verify").mock(
        return_value=httpx.Response(
            200,
            json={
                "valid": True,
                "message": "signature ok",
                "cert_id": "abc123",
                "verify_url": f"{BASE}/v/abc123",
            },
        )
    )
    with MeokClient() as c:
        result = c.verify({"cert_id": "abc123", "signature_sha256_hmac": "deadbeef"})
        assert isinstance(result, VerifyResult)
        assert result.valid is True
        assert result.cert_id == "abc123"


def test_verify_public_static(mocked_router: respx.MockRouter) -> None:
    mocked_router.post("/verify").mock(
        return_value=httpx.Response(200, json={"valid": False, "message": "expired"})
    )
    result = MeokClient.verify_public({"cert_id": "stale"})
    assert result.valid is False
    assert result.message == "expired"


# ── Async ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_async_verify(mocked_router: respx.MockRouter) -> None:
    mocked_router.post("/verify").mock(
        return_value=httpx.Response(200, json={"valid": True, "message": "ok"})
    )
    async with AsyncMeokClient() as c:
        result = await c.verify({"cert_id": "abc123"})
        assert result.valid is True


@pytest.mark.asyncio
async def test_async_sign_requires_key() -> None:
    async with AsyncMeokClient(api_key=None) as c:
        c.api_key = None
        with pytest.raises(MeokAuthError):
            await c.sign(regulation="GDPR", entity="X", score=50)
