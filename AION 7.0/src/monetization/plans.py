PLANS = [
    {"id": "starter", "name": "AEC Starter", "price_brl": 997, "price_usd": 249, "agents": ["#1"]},
    {"id": "professional", "name": "AEC Professional", "price_brl": 2391, "price_usd": 599, "agents": ["#1", "#2", "#3"]},
    {"id": "enterprise", "name": "AEC Enterprise", "price_brl": 4685, "price_usd": 1199, "agents": ["#1", "#2", "#3", "#4", "#5"]},
    {"id": "compliance_essencial", "name": "Compliance Essencial", "price_brl": 590, "price_usd": 149, "agents": ["#13", "#15"]},
    {"id": "regulatory_pro", "name": "Regulatory Pro", "price_brl": 1490, "price_usd": 379, "agents": ["#13", "#15", "#19", "#20", "#21"]},
    {"id": "esg_carbono", "name": "ESG + Carbono", "price_brl": 2490, "price_usd": 629, "agents": ["#16", "#17", "#18"]},
    {"id": "microsoft_pack", "name": "Microsoft Pack", "price_brl": 4482, "price_usd": 1129, "agents": ["#22", "#23", "#24", "#25", "#26", "#27"]},
    {"id": "tech_starter", "name": "Tech Starter", "price_brl": 1997, "price_usd": 499, "agents": ["#57"]},
    {"id": "tech_professional", "name": "Tech Professional", "price_brl": 3497, "price_usd": 899, "agents": ["#57", "#58", "#59"]},
    {"id": "tech_enterprise", "name": "Tech Enterprise", "price_brl": 5997, "price_usd": 1499, "agents": ["#57", "#58", "#59", "#49", "#50"]},
    {"id": "cross_sell_pack", "name": "Cross-Sell Pack", "price_brl": 297, "price_usd": 79, "agents": ["N1", "N2", "N3"]},
    {"id": "full_suite", "name": "Full Suite", "price_brl": 19997, "price_usd": 4999, "agents": ["all_71"]},
    {"id": "voice_receptionist_starter", "name": "AI Voice Receptionist", "price_brl": 0, "price_usd": 89, "agents": ["#64"]},
    {"id": "voice_receptionist_growth", "name": "AI Voice Receptionist — Growth", "price_brl": 0, "price_usd": 179, "agents": ["#64"]},
    # Wholesale tier for agency resellers (home services, real estate,
    # property management) -- requires a minimum 5-line commitment, priced
    # for real partner margin, not a race-to-bottom single-seat discount.
    {"id": "voice_receptionist_agency", "name": "AI Voice Receptionist — Agency Partner", "price_brl": 0, "price_usd": 59, "agents": ["#64"], "min_lines": 5},
]


def get_plan(plan_id: str) -> dict:
    return get_plan_by_id(plan_id)


def get_plan_by_id(plan_id: str) -> dict:
    for p in PLANS:
        if p["id"] == plan_id:
            return p
    return {}


def get_plan_by_price(price_brl: float) -> dict:
    for p in PLANS:
        if p["price_brl"] == price_brl:
            return p
    return {}
