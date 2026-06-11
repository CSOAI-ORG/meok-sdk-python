"""
MEOK Python SDK — Basic Usage Example
Demonstrates signing and verifying a compliance attestation.
"""

import os
from meok_sdk import MeokClient, CSOAIClient

# ── Configuration ────────────────────────────────────────────────────
API_KEY = os.getenv("MEOK_API_KEY", "sk_meok_demo_xxxxxxxx")

# ── 1. Sign a compliance attestation ────────────────────────────────
client = MeokClient(api_key=API_KEY)

cert = client.sign(
    regulation="EU_AI_ACT_ANNEX_III",
    entity="ACME Haulage Ltd",
    score=82,
    findings=[
        "Tachograph data exported successfully",
        "OCRS forecast: GREEN",
        "Driver CPC records up to date",
    ],
)

print("✅ Attestation signed")
print(f"   Cert ID : {cert.cert_id}")
print(f"   Score   : {cert.score}")
print(f"   Tier    : {cert.tier}")
print(f"   Verify  : {cert.verify_url}")

# ── 2. Public verification (no API key needed) ──────────────────────
result = MeokClient.verify_public(cert)
print(f"\n🔍 Verification result: {result.valid} — {result.message}")

# ── 3. CSOAI unified compliance client ──────────────────────────────
csoai = CSOAIClient(api_key=API_KEY)

# Check health
health = csoai.health()
print(f"\n🏥 CSOAI API health: {health.status}")

# Map a regulation across frameworks
mapping = csoai.map_framework(
    regulation="EU_AI_ACT_ART_50",
    frameworks=["ISO_42001", "NIST_AI_RMF", "TC260"],
)
print(f"\n📋 Framework mapping: {mapping.regulation}")
for row in mapping.crosswalk:
    print(f"   • {row.framework}: {row.mapped_clause} (gap: {row.gap_score})")
