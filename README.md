# meok-sdk

**Official Python SDK for the MEOK Attestation API** — sign + verify HMAC-signed compliance attestations across the MEOK trade-compliance ecosystem.

> Part of the [MEOK AI Labs](https://meok.ai) ecosystem powering [haulage.app](https://haulage.app), the umbrella for 32 PyPI-published Model Context Protocol servers covering UK + EU + US + AU + Canada + air + sea + rail trade compliance.

[![PyPI](https://img.shields.io/pypi/v/meok-sdk.svg)](https://pypi.org/project/meok-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/meok-sdk.svg)](https://pypi.org/project/meok-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)

## Install

```bash
pip install meok-sdk
```

Python ≥ 3.10. The only runtime dep is `httpx` — works in sync + async code, on Vercel Edge, AWS Lambda, anywhere modern Python runs.

## Quick start — verify a cert (no API key needed)

```python
from meok_sdk import MeokClient

cert = {  # came from any MEOK MCP tool result
    "cert_id": "...",
    "signature_sha256_hmac": "...",
    "payload": {...}
}

result = MeokClient.verify_public(cert)
print(result.valid, result.message)
```

The verifier endpoint is **public and rate-limited** — no auth, no install required beyond this package. That's the whole point: any auditor, regulator, or customer can verify your compliance chain from their machine.

## Sign a cert (requires an API key)

Get an API key by upgrading on [meok-compliance.vercel.app/pricing](https://meok-compliance.vercel.app/pricing) or [haulage.app/pricing](https://haulage.app/pricing). The key arrives in the welcome email after Stripe checkout.

```python
from meok_sdk import MeokClient

with MeokClient(api_key="sk_meok_…") as client:
    cert = client.sign(
        regulation="EU_AI_ACT_ANNEX_III",
        entity="ACME Haulage Ltd",
        score=82,
        findings=[
            "Tachograph data exported",
            "Driver hours within limits",
            "OCRS forecast GREEN",
        ],
        articles_audited=["Art_9", "Art_10", "Art_15"],
    )
    print(cert["verify_url"])  # share with auditor
```

You can also pass the key via the `MEOK_API_KEY` environment variable.

## Async usage

```python
import asyncio
from meok_sdk import AsyncMeokClient

async def main():
    async with AsyncMeokClient(api_key="sk_meok_…") as client:
        cert = await client.sign(regulation="GDPR", entity="ACME", score=92)
        verified = await client.verify(cert)
        assert verified.valid

asyncio.run(main())
```

## Error handling

All exceptions inherit from `MeokError`:

```python
from meok_sdk import (
    MeokAuthError,         # 401 — bad / missing API key
    MeokValidationError,   # 400 — missing fields / bad input
    MeokPaymentError,      # 402 — Stripe session not paid
    MeokAPIError,          # any other non-2xx
    MeokNetworkError,      # connect / DNS / TLS / timeout
    MeokError,             # catch-all base
)
```

## Environment variables

| Variable           | What                                                      | Default                                    |
|--------------------|-----------------------------------------------------------|--------------------------------------------|
| `MEOK_API_KEY`     | Default API key used when none is passed to the client.   | `None`                                     |
| `MEOK_API_BASE`    | Override base URL (testing, edge deployments).            | `https://meok-attestation-api.vercel.app`  |

## What gets signed

Every cert ships:

- `cert_id` — unique id
- `issued_at` / `expires_at` (~1 year)
- `regulation` / `entity` / `score` / `assessment` (COMPLIANT / PARTIAL / NON_COMPLIANT)
- `findings` / `articles_audited` / `auditor_notes`
- `issuer` / `kid` / `tier`
- `verify_url` — a public HTML page anyone can hit
- `signature_sha256_hmac` — base64url of HMAC-SHA256 over the canonical-JSON payload

The signing key never leaves the server. The verifier re-derives the canonical bytes and re-computes the HMAC; if they match, the cert holds.

## Related

- [MEOK Attestation API — OpenAPI 3.1 spec](https://meok-attestation-api.vercel.app/openapi.json)
- [Interactive docs (Swagger UI)](https://meok-attestation-api.vercel.app/docs)
- [Haulage.app — 32-MCP trade compliance catalogue](https://haulage.app)
- [Trust + security details](https://haulage.app/trust)
- [Source — github.com/CSOAI-ORG/meok-sdk-python](https://github.com/CSOAI-ORG/meok-sdk-python)

## License

MIT — © 2026 MEOK AI Labs / CSOAI LTD.
