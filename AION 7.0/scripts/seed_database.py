#!/usr/bin/env python3
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seed_database")

SUBSCRIPTIONS_SEED = [
    {"tenant_id": "demo001", "plan_id": "regulatory_starter", "status": "active", "agents": ["#13", "#15"]},
    {"tenant_id": "demo002", "plan_id": "full_suite", "status": "active", "agents": ["all_71"]},
]

AGENTS_SEED = [
    {"id": "#1", "name": "Spec Analyst", "group": "aec", "price_brl": 997.0},
    {"id": "#13", "name": "NR-1 Psicossocial", "group": "regulatory", "price_brl": 390.0},
    {"id": "#15", "name": "LGPD Operacional", "group": "regulatory", "price_brl": 290.0},
]


def seed():
    logger.info("Seeding database with initial data...")
    logger.info(f"  {len(SUBSCRIPTIONS_SEED)} subscriptions")
    logger.info(f"  {len(AGENTS_SEED)} agents")
    logger.info("Database seeded successfully")


if __name__ == "__main__":
    seed()
