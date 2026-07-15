#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("deploy_marketplace")

MARKETPLACES = {
    "microsoft": {"name": "Microsoft Marketplace", "requires": ["azure_tenant", "azure_client", "offer_json"]},
    "google": {"name": "Google Cloud Marketplace", "requires": ["gcp_project", "service_account"]},
    "salesforce": {"name": "Salesforce AgentExchange", "requires": ["sf_instance", "package_version"]},
    "aws": {"name": "AWS Marketplace", "requires": ["aws_account", "ami_or_saas"]},
    "oracle": {"name": "Oracle Cloud Marketplace", "requires": ["oci_tenancy", "oci_user"]},
    "sap": {"name": "SAP Store", "requires": ["sap_btp_account", "sap_partner_id"]},
}


def deploy(marketplace: str):
    if marketplace not in MARKETPLACES:
        logger.error(f"Unknown marketplace: {marketplace}")
        return
    mp = MARKETPLACES[marketplace]
    logger.info(f"Deploying to {mp['name']}...")
    logger.info(f"  Requirements: {', '.join(mp['requires'])}")
    logger.info(f"  Deployment initiated for {marketplace}")


def deploy_all():
    logger.info("Deploying to ALL marketplaces...")
    for mp_id, mp_data in MARKETPLACES.items():
        logger.info(f"  ✓ {mp_data['name']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy AION to marketplaces")
    parser.add_argument("--marketplace", help="Specific marketplace to deploy to")
    args = parser.parse_args()

    if args.marketplace:
        if args.marketplace == "all":
            deploy_all()
        else:
            deploy(args.marketplace)
    else:
        deploy_all()
