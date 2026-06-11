"""Sync + async clients for the CSOAI public API.

Both clients share the same surface:

    * ``get_compliance_map()``          — fetch the global compliance map
    * ``get_crosswalk()``               — fetch framework crosswalk data
    * ``get_dome_status()``             — DOME engine status
    * ``get_council_votes()``           — council vote records
    * ``verify_sigil(sigil_id)``        — verify a sigil identifier
    * ``get_region(code)``              — lookup a single region from the map
    * ``get_regulatory_countdowns()``   — upcoming regulatory deadlines
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import httpx

from .errors import CSOAINetworkError, from_response
from .models import (
    ComplianceMap,
    CouncilVote,
    CrosswalkRow,
    DOMEStatus,
    Region,
    RegulatoryCountdown,
    SigilVerification,
)

DEFAULT_BASE_URL = "https://csoai.org"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "meok-sdk-python/0.1.1"


def _build_headers(api_key: str | None) -> dict[str, str]:
    h: dict[str, str] = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if api_key:
        h["X-API-Key"] = api_key
    return h


def _check(response: httpx.Response) -> dict[str, Any]:
    """Raise on non-2xx, otherwise return parsed JSON."""
    try:
        body = response.json()
    except Exception:
        body = {"error": response.text}
    if response.status_code >= 400:
        raise from_response(response.status_code, body)
    return body


class CSOAIClient:
    """Synchronous client for the CSOAI public API. Backed by ``httpx.Client``.

    Use as a context manager to ensure connection-pool cleanup::

        with CSOAIClient(api_key="optional") as client:
            map_data = client.get_compliance_map()
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("CSOAI_API_KEY")
        self.base_url = (base_url or os.environ.get("CSOAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._http = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
            headers={"User-Agent": USER_AGENT},
        )

    # ── Context manager + close ──────────────────────────────────────
    def __enter__(self) -> "CSOAIClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    # ── Internal helpers ───────────────────────────────────────────────
    def _get(self, path: str) -> dict[str, Any]:
        try:
            response = self._http.get(path, headers=_build_headers(self.api_key))
        except httpx.HTTPError as e:
            raise CSOAINetworkError(str(e)) from e
        return _check(response)

    # ── Public surface ─────────────────────────────────────────────────
    def get_compliance_map(self) -> ComplianceMap:
        """Fetch the global compliance map.

        Returns:
            A :class:`ComplianceMap` containing regions and frameworks.
        """
        body = self._get("/api/map.json")
        return ComplianceMap.from_json(body)

    def get_crosswalk(self) -> list[CrosswalkRow]:
        """Fetch the framework crosswalk data.

        Returns:
            A list of :class:`CrosswalkRow` mappings between frameworks.
        """
        body = self._get("/api/crosswalk.json")
        rows = body.get("rows", body) if isinstance(body, dict) else body
        if not isinstance(rows, list):
            rows = []
        return [CrosswalkRow.from_json(r) for r in rows]

    def get_dome_status(self) -> DOMEStatus:
        """Fetch the DOME engine status.

        Returns:
            A :class:`DOMEStatus` with current operational metrics.
        """
        body = self._get("/api/dome/status.json")
        return DOMEStatus.from_json(body)

    def get_council_votes(self) -> list[CouncilVote]:
        """Fetch council vote records.

        Returns:
            A list of :class:`CouncilVote` records.
        """
        body = self._get("/api/council/votes.json")
        votes = body.get("votes", body) if isinstance(body, dict) else body
        if not isinstance(votes, list):
            votes = []
        return [CouncilVote.from_json(v) for v in votes]

    def verify_sigil(self, sigil_id: str) -> SigilVerification:
        """Verify a sigil / certification identifier.

        Args:
            sigil_id: The sigil identifier to verify (e.g. ``"WD-2026-001"``).

        Returns:
            A :class:`SigilVerification` result.
        """
        body = self._get(f"/api/sigil/verify.json?id={quote(sigil_id, safe='')}")
        return SigilVerification.from_json(body)

    def get_region(self, code: str) -> Region | None:
        """Lookup a single region from the compliance map.

        Args:
            code: Region code, e.g. ``"eu"``, ``"uk"``, ``"us"``.

        Returns:
            The matching :class:`Region` or ``None`` if not found.
        """
        cmap = self.get_compliance_map()
        code_lower = code.lower()
        for region in cmap.regions:
            if region.code.lower() == code_lower:
                return region
        return None

    def get_regulatory_countdowns(self) -> list[RegulatoryCountdown]:
        """Fetch upcoming regulatory deadlines.

        Returns:
            A list of :class:`RegulatoryCountdown` items.
        """
        body = self._get("/api/countdowns.json")
        items = body.get("countdowns", body) if isinstance(body, dict) else body
        if not isinstance(items, list):
            items = []
        return [RegulatoryCountdown.from_json(c) for c in items]


class AsyncCSOAIClient:
    """Async mirror of :class:`CSOAIClient`. Backed by ``httpx.AsyncClient``.

    ::

        async with AsyncCSOAIClient(api_key="optional") as client:
            map_data = await client.get_compliance_map()
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("CSOAI_API_KEY")
        self.base_url = (base_url or os.environ.get("CSOAI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
            headers={"User-Agent": USER_AGENT},
        )

    async def __aenter__(self) -> "AsyncCSOAIClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    # ── Internal helpers ───────────────────────────────────────────────
    async def _get(self, path: str) -> dict[str, Any]:
        try:
            response = await self._http.get(path, headers=_build_headers(self.api_key))
        except httpx.HTTPError as e:
            raise CSOAINetworkError(str(e)) from e
        return _check(response)

    # ── Public surface ─────────────────────────────────────────────────
    async def get_compliance_map(self) -> ComplianceMap:
        """Fetch the global compliance map (async)."""
        body = await self._get("/api/map.json")
        return ComplianceMap.from_json(body)

    async def get_crosswalk(self) -> list[CrosswalkRow]:
        """Fetch the framework crosswalk data (async)."""
        body = await self._get("/api/crosswalk.json")
        rows = body.get("rows", body) if isinstance(body, dict) else body
        if not isinstance(rows, list):
            rows = []
        return [CrosswalkRow.from_json(r) for r in rows]

    async def get_dome_status(self) -> DOMEStatus:
        """Fetch the DOME engine status (async)."""
        body = await self._get("/api/dome/status.json")
        return DOMEStatus.from_json(body)

    async def get_council_votes(self) -> list[CouncilVote]:
        """Fetch council vote records (async)."""
        body = await self._get("/api/council/votes.json")
        votes = body.get("votes", body) if isinstance(body, dict) else body
        if not isinstance(votes, list):
            votes = []
        return [CouncilVote.from_json(v) for v in votes]

    async def verify_sigil(self, sigil_id: str) -> SigilVerification:
        """Verify a sigil / certification identifier (async)."""
        body = await self._get(f"/api/sigil/verify.json?id={quote(sigil_id, safe='')}")
        return SigilVerification.from_json(body)

    async def get_region(self, code: str) -> Region | None:
        """Lookup a single region from the compliance map (async)."""
        cmap = await self.get_compliance_map()
        code_lower = code.lower()
        for region in cmap.regions:
            if region.code.lower() == code_lower:
                return region
        return None

    async def get_regulatory_countdowns(self) -> list[RegulatoryCountdown]:
        """Fetch upcoming regulatory deadlines (async)."""
        body = await self._get("/api/countdowns.json")
        items = body.get("countdowns", body) if isinstance(body, dict) else body
        if not isinstance(items, list):
            items = []
        return [RegulatoryCountdown.from_json(c) for c in items]
