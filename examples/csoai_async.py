"""
MEOK Python SDK — Async Usage Example
Demonstrates async signing, verification, and batch operations.
"""

import asyncio
import os
from meok_sdk import AsyncMeokClient, AsyncCSOAIClient

API_KEY = os.getenv("MEOK_API_KEY", "sk_meok_demo_xxxxxxxx")


async def main():
    # ── 1. Async attestation signing ───────────────────────────────
    async with AsyncMeokClient(api_key=API_KEY) as client:
        cert = await client.sign(
            regulation="UK_AI_BILL",
            entity="NetworkNick Logistics",
            score=91,
            findings=["DVSA Earned Recognition compliant", "FOR Silver achieved"],
        )
        print(f"✅ Signed: {cert.cert_id} (score={cert.score})")

        # ── 2. Async public verification ───────────────────────────
        result = await client.verify_public(cert)
        print(f"🔍 Verified: {result.valid} — {result.message}")

    # ── 3. Batch sign multiple entities ────────────────────────────
    entities = [
        ("Fleet A", 88, "EU_AI_ACT_ANNEX_III"),
        ("Fleet B", 74, "EU_AI_ACT_ANNEX_IV"),
        ("Fleet C", 95, "NIST_AI_RMF"),
    ]

    async with AsyncMeokClient(api_key=API_KEY) as client:
        tasks = [
            client.sign(
                regulation=reg,
                entity=name,
                score=score,
                findings=[f"Automated assessment for {name}"],
            )
            for name, score, reg in entities
        ]
        certs = await asyncio.gather(*tasks)

    print("\n📦 Batch results:")
    for c in certs:
        print(f"   • {c.entity}: {c.score} → {c.assessment}")

    # ── 4. Async CSOAI cross-regional handoff ──────────────────────
    async with AsyncCSOAIClient(api_key=API_KEY) as csoai:
        handoff = await csoai.cross_regional_handoff(
            cert_id=certs[0].cert_id,
            from_region="EU",
            to_region="UK",
        )
        print(f"\n🌍 Handoff: {handoff.status} — {handoff.message}")


if __name__ == "__main__":
    asyncio.run(main())
