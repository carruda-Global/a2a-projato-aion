import json
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError

from src.config import Settings

logger = logging.getLogger(__name__)


class AWSMarketplaceClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.aws_region = settings.aws_region
        self.product_code = settings.aws_product_code
        self.sns_topic_arn = settings.aws_sns_topic_arn

        session_kwargs = {"region_name": self.aws_region}
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self.session = boto3.Session(**session_kwargs)
        self.metering_client = self.session.client("marketplace-metering")
        self.entitlement_client = self.session.client("marketplace-entitlement")

    def resolve_customer(self, registration_token: str) -> dict[str, Any] | None:
        try:
            response = self.metering_client.resolve_customer(
                RegistrationToken=registration_token
            )
            return {
                "customer_id": response["CustomerIdentifier"],
                "product_code": response["ProductCode"],
                "customer_aws_account_id": response.get("CustomerAWSAccountId", ""),
            }
        except ClientError as e:
            logger.error("Erro ao resolver customer AWS: %s", e)
            return None

    def get_entitlement(
        self, customer_id: str
    ) -> dict[str, Any] | None:
        try:
            response = self.entitlement_client.get_entitlements(
                ProductCode=self.product_code,
                Filter={"CUSTOMER_IDENTIFIER": [customer_id]},
            )
            entitlements = response.get("Entitlements", [])
            if not entitlements:
                return None

            entitlement = entitlements[0]
            dimension = entitlement.get("Dimension", "")
            expiration = entitlement.get("ExpirationDate")
            status = "Active" if expiration is None else "Expired"

            return {
                "customer_id": customer_id,
                "product_code": self.product_code,
                "dimension": dimension,
                "status": status,
                "expiration": str(expiration) if expiration else None,
            }
        except ClientError as e:
            logger.error("Erro ao verificar entitlement AWS: %s", e)
            return None

    def is_subscription_active(self, customer_id: str) -> bool:
        entitlement = self.get_entitlement(customer_id)
        if not entitlement:
            return False
        return entitlement["status"] == "Active"

    def process_sns_notification(self, message: dict) -> dict[str, Any]:
        message_type = message.get("MessageType", "")
        message_content = json.loads(message.get("Message", "{}"))

        action = message_content.get("action", "")

        logger.info("SNS AWS Marketplace: type=%s action=%s", message_type, action)

        return {
            "type": message_type,
            "action": action,
            "customer_id": message_content.get("CustomerIdentifier", ""),
            "product_code": message_content.get("ProductCode", ""),
        }
