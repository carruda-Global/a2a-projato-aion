import asyncio
from workers.linkedin.integrations.config import LinkedInConfig
from workers.linkedin.integrations.oauth import LinkedInOAuth
from workers.linkedin.integrations.tools import LinkedInTools

TEXT = (
    "We just published the full guide to AI phone receptionists — cost breakdowns, "
    "security/privacy details, industry fit, and honest comparisons vs. voicemail and "
    "traditional answering services.\n\n"
    "If you're evaluating an AI receptionist for your business (or just curious how "
    "the category actually works), it's a straight answer, not a sales page.\n\n"
    "Built AION Voice Receptionist around the same questions people actually ask before buying: "
    "will it really answer every call, what happens when it can't help, and how much does it "
    "actually cost vs. hiring staff.\n\n"
    "Full guide + live demo line you can call right now:"
)
LINK = "https://global-engenharia.com/ai-receptionist-guide.html"


async def main():
    config = LinkedInConfig()
    oauth = LinkedInOAuth(config)
    tools = LinkedInTools(config, oauth)
    result = await tools.create_post(
        text=TEXT,
        link_url=LINK,
        link_title="The Complete AI Receptionist Guide",
        link_description="Cost, security, industry fit, and comparisons — the full guide to AI phone receptionists.",
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
