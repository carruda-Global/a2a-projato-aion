"""One-off: publish the English AION Voice Receptionist post (US/UK/CA/AU
small-business audience), using the real LinkedIn agent, not the browser."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from integrations import LinkedInIntegration, LinkedInConfig

TEXT = """Every missed call is a customer who just called your competitor instead.

Small businesses lose an average of 30%+ of inbound calls to voicemail -- and most callers never call back.

We built AION Voice Receptionist to fix that: answers every call 24/7, texts back missed calls instantly with a booking link, captures the lead's name and reason for calling. No developer, no long contract -- live in under 20 minutes.

Don't take our word for it -- call the live demo right now and judge the voice quality yourself: +1 (406) 602-9130

Free trial:"""

LINK = "https://global-engenharia.com/vendas.html"


async def main():
    linkedin = LinkedInIntegration(config=LinkedInConfig())
    await linkedin.initialize()
    try:
        result = await linkedin.tools.create_post(
            text=TEXT,
            link_url=LINK,
            link_title="AION Voice Receptionist -- Never Miss a Call Again",
            link_description="24/7 AI phone receptionist for small businesses. Live in under 20 minutes, no developer needed.",
        )
        print("POST RESULT:", result)
    finally:
        await linkedin.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
