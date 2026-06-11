"""Sync + async clients for the MEOK Attestation API.

Both clients share the same surface:

    * ``sign(...)``       — issue a signed cert (auth required)
    * ``verify(cert)``    — verify a signed cert (no auth)
    * ``provision(...)``  — exchange a paid Stripe session for an API key
    * ``health()``        — liveness probe

There is also a static helper :py:meth:`MeokClient.verify_public` for one-shot
verification without instantiating a client.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from .errors import MeokNetworkError, from_response
from .models import Cert, SignRequest, VerifyResult

DEFAULT_BASE_URL = "https://meok-attestation-api.vercel.app"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "meok-sdk-python/0.1.1"


def _build_headers(api_key: str | None, extra: dict[str, str] | None = None) -> dict[str, str]:
    h: dict[str, str] = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if api_key:
        h["X-API-Key"] = api_key
    if extra:
        h.update(extra)
    return h


def _check(response: httpx.Response) -> dict[str, Any]:
    """Raise on non-2xx, otherwise return parsed JSON."""
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 — many APIs return text on error
        body = {"error": response.text}
    if response.status_code >= 400:
        raise from_response(response.status_code, body)
    return body


class MeokClient:
    """Synchronous client. Backed by ``httpx.Client``.

    Use as a context manager to ensure connection-pool cleanup::

        with MeokClient(api_key="sk_meok_…") as client:
            cert = client.sign(regulation="GDPR", entity="ACME", score=80)
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("MEOK_API_KEY")
        self.base_url = (base_url or os.environ.get("MEOK_API_BASE") or DEFAULT_BASE_URL).rstrip("/")
        self._http = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
            headers={"User-Agent": USER_AGENT},
        )

    # ── Context manager + close ──────────────────────────────────────
    def __enter__(self) -> "MeokClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    # ── Public surface ───────────────────────────────────────────────
    def health(self) -> dict[str, Any]:
        try:
            response = self._http.get("/health", headers=_build_headers(None))
        except httpx.HTTPError as e:
            raise MeokNetworkError(str(e)) from e
        return _check(response)

    def sign(
        self,
        *,
        regulation: str,
        entity: str,
        score: float,
        findings: list[str] | None = None,
        articles_audited: list[str] | None = None,
        auditor_notes: str = "",
        email: str | None = None,
    ) -> Cert:
        if not self.api_key:
            from .errors import MeokAuthError

            raise MeokAuthError(401, "MeokClient.sign requires an api_key.", body=None)

        body = SignRequest(
            regulation=regulation,
            entity=entity,
            score=score,
            findings=findings or [],
            articles_audited=articles_audited or [],
            auditor_notes=auditor_notes,
        ).to_json()
        body["api_key"] = self.api_key
        if email:
            body["email"] = email

        try:
            response = self._http.post(
                "/sign", headers=_build_headers(self.api_key), json=body
            )
        except httpx.HTTPError as e:
            raise MeokNetworkError(str(e)) from e
        return _check(response)  # type: ignore[return-value]

    def verify(self, cert: Cert | dict[str, Any]) -> VerifyResult:
        try:
            response = self._http.post(
                "/verify", headers=_build_headers(None), json=dict(cert)
            )
        except httpx.HTTPError as e:
            raise MeokNetworkError(str(e)) from e
        return VerifyResult.from_json(_check(response))

    def provision(
        self,
        *,
        session_id: str | None = None,
        master_key: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if session_id:
            body["session_id"] = session_id
        if email:
            body["email"] = email
        headers = _build_headers(None)
        if master_key:
            headers["X-Master-Key"] = master_key

        try:
            response = self._http.post("/provision", headers=headers, json=body)
        except httpx.HTTPError as e:
            raise MeokNetworkError(str(e)) from e
        return _check(response)

    # ── Static helper — verification without an instance ─────────────
    @staticmethod
    def verify_public(
        cert: Cert | dict[str, Any],
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> VerifyResult:
        """One-shot public verification — no API key, no client setup."""
        try:
            response = httpx.post(
                f"{base_url.rstrip('/')}/verify",
                json=dict(cert),
                timeout=timeout,
                headers=_build_headers(None),
            )
        except httpx.HTTPError as e:
            raise MeokNetworkError(str(e)) from e
        return VerifyResult.from_json(_check(response))


class AsyncMeokClient:
    """Async mirror of :class:`MeokClient`. Backed by ``httpx.AsyncClient``.

    ::

        async with AsyncMeokClient(api_key="sk_meok_…") as client:
            cert = await client.sign(regulation="GDPR", entity="ACME", score=80)
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("MEOK_API_KEY")
        self.base_url = (base_url or os.environ.get("MEOK_API_BASE") or DEFAULT_BASE_URL).rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
            headers={"User-Agent": USER_AGENT},
        )

    async def __aenter__(self) -> "AsyncMeokClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def health(self) -> dict[str, Any]:
        try:
            response = await self._http.get("/health", headers=_build_headers(None))
        except httpx.HTTPError as e:
            raise MeokNetworkError(str(e)) from e
        return _check(response)

    async def sign(
        self,
        *,
        regulation: str,
        entity: str,
        score: float,
        findings: list[str] | None = None,
        articles_audited: list[str] | None = None,
        auditor_notes: str = "",
        email: str | None = None,
    ) -> Cert:
        if not self.api_key:
            from .errors import MeokAuthError

            raise MeokAuthError(401, "AsyncMeokClient.sign requires an api_key.", body=None)

        body = SignRequest(
            regulation=regulation,
            entity=entity,
            score=score,
            findings=findings or [],
            articles_audited=articles_audited or [],
            auditor_notes=auditor_notes,
        ).to_json()
        body["api_key"] = self.api_key
        if email:
            body["email"] = email

        try:
            response = await self._http.post(
                "/sign", headers=_build_headers(self.api_key), json=body
            )
        except httpx.HTTPError as e:
            raise MeokNetworkError(str(e)) from e
        return _check(response)  # type: ignore[return-value]

    async def verify(self, cert: Cert | dict[str, Any]) -> VerifyResult:
        try:
            response = await self._http.post(
                "/verify", headers=_build_headers(None), json=dict(cert)
            )
        except httpx.HTTPError as e:
            raise MeokNetworkError(str(e)) from e
        return VerifyResult.from_json(_check(response))

    async def provision(
        self,
        *,
        session_id: str | None = None,
        master_key: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if session_id:
            body["session_id"] = session_id
        if email:
            body["email"] = email
        headers = _build_headers(None)
        if master_key:
            headers["X-Master-Key"] = master_key

        try:
            response = await self._http.post("/provision", headers=headers, json=body)
        except httpx.HTTPError as e:
            raise MeokNetworkError(str(e)) from e
        return _check(response)
