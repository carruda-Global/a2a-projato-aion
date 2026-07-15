import json
from pathlib import Path

OFFERS_DIR = Path(__file__).parent.parent / "offers"
OFFER_PATH = OFFERS_DIR / "aion-71-agentes-offer.json"

ENTERPRISE_PLANS = [
    {"id": "governance_starter", "name": "Governance Starter", "price_brl": 199700, "price_usd": 49900, "agents": ["#60"]},
    {"id": "governance_pro", "name": "Governance Pro", "price_brl": 597000, "price_usd": 149000, "agents": ["#60"]},
    {"id": "governance_enterprise", "name": "Governance Enterprise", "price_brl": 999700, "price_usd": 249900, "agents": ["#60"]},
    {"id": "bridge_starter", "name": "Bridge Starter", "price_brl": 196000, "price_usd": 49000, "agents": ["#61"]},
    {"id": "bridge_pro", "name": "Bridge Pro", "price_brl": 597000, "price_usd": 149000, "agents": ["#61"]},
    {"id": "bridge_enterprise", "name": "Bridge Enterprise", "price_brl": 797000, "price_usd": 199000, "agents": ["#61"]},
    {"id": "reviewer_starter", "name": "Reviewer Starter", "price_brl": 39600, "price_usd": 9900, "agents": ["#62"]},
    {"id": "reviewer_pro", "name": "Reviewer Pro", "price_brl": 119700, "price_usd": 29900, "agents": ["#62"]},
    {"id": "reviewer_enterprise", "name": "Reviewer Enterprise", "price_brl": 199700, "price_usd": 49900, "agents": ["#62"]},
    {"id": "enterprise_full", "name": "Enterprise Full Suite", "price_brl": 1597000, "price_usd": 399900, "agents": ["#60", "#61", "#62"]},
]

with open(OFFER_PATH, encoding="utf-8") as f:
    offer = json.load(f)

for mp in ["microsoft", "google", "salesforce", "aws", "oracle", "sap"]:
    if mp in offer["marketplaces"]:
        offer["marketplaces"][mp]["plans"].extend(ENTERPRISE_PLANS)

offer["name"] = "AION - 74 Agentes de IA"
offer["version"] = "6.1"

with open(OFFER_PATH, "w", encoding="utf-8") as f:
    json.dump(offer, f, indent=2, ensure_ascii=False)

print(f"[OK] Offer atualizada com {len(ENTERPRISE_PLANS)} planos enterprise")
print(f"  Total de planos: {sum(len(mp['plans']) for mp in offer['marketplaces'].values())}")
