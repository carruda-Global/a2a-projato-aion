import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PrivacyEmailService:

    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY", "")
        self.from_email = os.getenv("EMAIL_FROM", "privacy@aion.global")
        self.client = None
        if self.api_key:
            try:
                from sendgrid import SendGridAPIClient
                self.client = SendGridAPIClient(self.api_key)
            except ImportError:
                logger.warning("sendgrid not installed")

    def send_consent_confirmation(self, email: str, user_name: str) -> bool:
        if not self.client:
            logger.info(f"[EMAIL] Consent confirmation to {email} - sendgrid not configured")
            return False
        try:
            from sendgrid.helpers.mail import Mail
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject="Confirmacao de Consentimento - AION",
                html_content=f"<h1>Confirmacao de Consentimento</h1><p>Ola {user_name},</p><p>Registramos seu consentimento para a Politica de Privacidade e Termos de Uso da AION.</p><p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p><p>Voce pode revogar seu consentimento a qualquer momento.</p>"
            )
            self.client.send(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send consent email: {e}")
            return False

    def send_consent_revoked(self, email: str, user_name: str) -> bool:
        if not self.client:
            logger.info(f"[EMAIL] Consent revoked notification to {email} - sendgrid not configured")
            return False
        try:
            from sendgrid.helpers.mail import Mail
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject="Consentimento Revogado - AION",
                html_content=f"<h1>Consentimento Revogado</h1><p>Ola {user_name},</p><p>Recebemos sua solicitacao de revogacao de consentimento.</p><p>Seus dados serao excluidos ou anonimizados conforme a LGPD.</p>"
            )
            self.client.send(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send revocation email: {e}")
            return False
