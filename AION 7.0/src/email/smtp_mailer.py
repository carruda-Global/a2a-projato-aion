import os
import smtplib
from email.mime.text import MIMEText

HOSTINGER_EMAIL_USER = os.getenv("HOSTINGER_EMAIL_USER", "")
HOSTINGER_EMAIL_PASSWORD = os.getenv("HOSTINGER_EMAIL_PASSWORD", "")


def send_via_hostinger(to_email: str, subject: str, html_body: str) -> None:
    """Confirmed-working send path (Resend's domain is still unverified — see
    stripe_webhook.py history). Raises on failure; callers decide how to log it."""
    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = HOSTINGER_EMAIL_USER
    msg["To"] = to_email
    server = smtplib.SMTP("smtp.hostinger.com", 587, timeout=15)
    server.starttls()
    server.login(HOSTINGER_EMAIL_USER, HOSTINGER_EMAIL_PASSWORD)
    server.sendmail(HOSTINGER_EMAIL_USER, [to_email], msg.as_string())
    server.quit()
