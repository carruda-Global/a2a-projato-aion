"""Bulk SEO page generation — resumable CLI driver over src/agents/seo_topics.py.

Usage:
    python scripts/generate_seo_pages.py --dry-run
    python scripts/generate_seo_pages.py --region BR --limit 40
    python scripts/generate_seo_pages.py --product engineering_suite
    python scripts/generate_seo_pages.py --kind capability --region US,BR

Safe to re-run: generate_market_pages() already skips slugs that exist in
the DB, so a crashed/interrupted run just picks up where it left off.
"""
import argparse
import asyncio
import sys

sys.path.insert(0, ".")

from src.config import Settings
from src.agents.seo_content_agent import SEOContentAgent, plan_slugs
from src.agents.seo_topics import ALL_MARKETS


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--region", type=str, default=None, help="Comma-separated market codes (default: all)")
    p.add_argument("--product", type=str, default=None, help="Only this product key")
    p.add_argument("--kind", type=str, choices=["regulation", "capability"], default=None)
    p.add_argument("--limit", type=int, default=None, help="Max new pages generated PER region this run")
    p.add_argument("--dry-run", action="store_true", help="Print the plan, make no LLM/DB calls")
    return p.parse_args()


async def main():
    args = parse_args()
    regions = tuple(args.region.split(",")) if args.region else ALL_MARKETS

    if args.dry_run:
        grand_total = 0
        for market in regions:
            plan = plan_slugs(market, args.product, args.kind)
            print(f"\n=== {market}: {len(plan)} planned slugs ===")
            for topic, sector, size_key, size_label, slug in plan[:5]:
                print(f"  {slug}  [{topic.kind} -> {topic.product}]")
            if len(plan) > 5:
                print(f"  ... +{len(plan) - 5} more")
            grand_total += len(plan)
        print(f"\nTOTAL planned across {len(regions)} region(s): {grand_total}")
        print("(This does not account for slugs that already exist in the DB — "
              "those are skipped automatically at generation time.)")
        return

    settings = Settings()
    agent = SEOContentAgent(settings)
    grand_generated = 0
    grand_skipped = 0
    for market in regions:
        print(f"\n=== Generating {market} ===")
        result = await agent.generate_market_pages(
            market, product_filter=args.product, kind_filter=args.kind, limit=args.limit,
        )
        if "error" in result:
            print(f"  {result['error']}")
            continue
        print(f"  generated={result['pages_generated']} skipped={result['pages_skipped']}")
        grand_generated += result["pages_generated"]
        grand_skipped += result["pages_skipped"]

    print(f"\nTOTAL generated={grand_generated} skipped={grand_skipped}")


if __name__ == "__main__":
    asyncio.run(main())
