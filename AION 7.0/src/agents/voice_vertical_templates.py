"""Real starter knowledge per vertical, seeded into a new customer's RAG
via the existing voice_rag.ingest_knowledge() pipeline at signup. This is
the actual premium differentiator for agency-reseller deals: a plumber's
receptionist already knows how to triage an emergency leak on day one,
instead of an agency handing their client a blank FAQ box to fill in
themselves -- which is what every generic competitor makes them do."""
from src.agents.voice_rag import ingest_knowledge

VERTICAL_TEMPLATES: dict[str, str] = {
    "home_services": """
Emergency triage: if the caller mentions active water leak, no heat in freezing weather,
no AC in extreme heat, gas smell, sparking outlet, or total power loss, mark this as
URGENT and say a technician will call back within 30 minutes -- do not just take a message.
Non-emergency requests (routine maintenance, tune-ups, estimates) get scheduled for the
next available slot, no rush framing.

For quote requests: ask for the type of service (repair vs. installation vs. inspection),
the equipment involved if known (brand/age of unit), and whether they've had this issue
before. Don't quote a price on the phone -- say a technician will provide a firm quote
after a brief on-site or photo assessment.

Always confirm: service address, best callback number, and whether the property is
owner-occupied or a rental (rental issues often need landlord authorization before work
starts).

Standard questions callers ask: "Are you licensed and insured?" -- yes, confirm the
business carries full licensing and insurance, details available on request. "Do you
offer emergency/weekend service?" -- confirm based on what the business owner has set
up; if unknown, say someone will confirm shortly. "What's your service area?" -- ask
for their zip code and confirm coverage.
""".strip(),

    "real_estate": """
First, determine if the caller is a buyer, a seller, a renter, or an existing client
following up -- the right next step is different for each.

Buyers: ask what price range, area/neighborhood, and property type (single-family,
condo, etc.) they're interested in, and whether they're pre-approved for financing.
Offer to schedule a showing or connect them with an agent for a buyer consultation.

Sellers: ask for the property address and whether they're just curious about value or
ready to list. Offer a callback from an agent for a market analysis, don't attempt to
estimate value yourself.

Renters: ask what they're looking for (bedrooms, budget, move-in date) and whether
they've seen a specific listing. Offer to schedule a showing.

Showing requests: confirm the property address or listing they saw, their availability
(day/time windows), and whether they're working with an agent already (avoid
double-booking or stepping on another agent's client relationship).

After-hours calls: confirm office hours and offer to schedule a callback for the next
business day unless the caller says it's time-sensitive (e.g., an offer deadline).
""".strip(),

    "property_management": """
Maintenance requests are the most common call type -- always ask: is this urgent
(no heat/AC in extreme weather, active leak, no working toilet, lockout, broken lock/
door, gas smell) or routine (minor repair, cosmetic issue, appliance not working but
not urgent)? Urgent requests get escalated for same-day or emergency response; routine
requests get logged for the standard maintenance queue.

Always collect: unit/property address, tenant name, and a callback number, plus a clear
description of the issue.

Rent payment questions: don't process payments by phone. Direct callers to the tenant
portal or confirm a callback from the office for payment arrangements.

Move-in/move-out questions: collect the property address and date, and offer a callback
from the leasing team -- don't attempt to quote move-out charges or deposit amounts
yourself.

Prospective tenant inquiries (not an existing tenant): ask what property/unit they're
interested in, move-in timeline, and offer to schedule a showing or connect with
leasing.
""".strip(),
}


async def seed_vertical_knowledge(customer_email: str, location_label: str, vertical: str) -> int:
    """Seeds a new customer's RAG with real, vertical-specific starter
    knowledge. Returns chunks stored (0 if vertical is unrecognized or
    ingestion fails -- never blocks provisioning)."""
    template = VERTICAL_TEMPLATES.get(vertical)
    if not template:
        return 0
    return await ingest_knowledge(customer_email, location_label, template)
