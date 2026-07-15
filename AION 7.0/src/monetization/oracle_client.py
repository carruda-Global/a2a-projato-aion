import logging
from typing import Any

import oci

from src.config import Settings

logger = logging.getLogger(__name__)


class OracleMarketplaceClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.product_id = settings.oracle_product_id
        self.seller_id = settings.oracle_seller_id
        self.self_client = None

        config = self._build_config(settings)
        signer = self._build_signer(settings)

        try:
            if signer:
                self.self_client = oci.self.PartnerIntegerationClient(
                    config={}, signer=signer
                )
            else:
                self.self_client = oci.self.PartnerIntegerationClient(config)
        except oci.exceptions.InvalidConfig as e:
            logger.warning("OCI config invalida: %s", e)

    def _build_config(self, settings: Settings) -> dict:
        config = {}
        if settings.oci_config_file:
            try:
                config = oci.config.from_file(
                    settings.oci_config_file, settings.oci_profile
                )
            except Exception as e:
                logger.warning("Erro ao carregar config OCI: %s", e)
        return config

    def _build_signer(self, settings: Settings) -> Any | None:
        if settings.oci_use_instance_principal:
            try:
                return oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            except Exception as e:
                logger.warning("Erro InstancePrincipal OCI: %s", e)
        if settings.oci_use_resource_principal:
            try:
                return oci.auth.signers.ResourcePrincipalsSecurityTokenSigner()
            except Exception as e:
                logger.warning("Erro ResourcePrincipal OCI: %s", e)
        return None

    def _check_client(self) -> bool:
        if self.self_client is None:
            logger.error("OCI client nao inicializado (config invalida)")
            return False
        return True

    def resolve_subscription(self, self_token: str) -> dict[str, Any] | None:
        if not self._check_client():
            return None
        try:
            response = self.self_client.resolve_subscription(
                product_id=self.product_id,
                self_token=self_token,
            )
            data = response.data
            sub = data.subscription
            return {
                "subscription_id": sub.id,
                "product_id": self.product_id,
                "customer_tenancy_id": sub.tenant_id,
                "plan_name": sub.subscription_details.get("plan_name", ""),
                "plan_id": sub.subscription_details.get("plan_id", ""),
                "state": sub.lifecycle_state,
            }
        except oci.exceptions.ServiceError as e:
            logger.error("Erro ao resolver subscription Oracle: %s", e)
            return None

    def activate_subscription(self, subscription_id: str) -> bool:
        if not self._check_client():
            return False
        try:
            self.self_client.activate_subscription(
                product_id=self.product_id,
                subscription_id=subscription_id,
            )
            logger.info("Subscription ativada Oracle: %s", subscription_id)
            return True
        except oci.exceptions.ServiceError as e:
            logger.error("Erro ao ativar subscription Oracle: %s", e)
            return False

    def list_subscriptions(self) -> list[dict[str, Any]]:
        if not self._check_client():
            return []
        try:
            response = self.self_client.listing_subscriptions(
                listing_id=self.product_id
            )
            subs = []
            for item in response.data.items:
                subs.append({
                    "subscription_id": item.id,
                    "tenant_id": item.tenant_id,
                    "state": item.lifecycle_state,
                    "time_created": str(item.time_created) if item.time_created else None,
                })
            return subs
        except oci.exceptions.ServiceError as e:
            logger.error("Erro ao listar subscriptions Oracle: %s", e)
            return []

    def is_subscription_active(self, subscription_id: str) -> bool:
        if not self._check_client():
            return False
        try:
            response = self.self_client.get_subscription(
                subscription_id=subscription_id,
                product_id=self.product_id,
            )
            return response.data.lifecycle_state == "ACTIVE"
        except oci.exceptions.ServiceError as e:
            logger.error("Erro ao verificar subscription Oracle: %s", e)
            return False
