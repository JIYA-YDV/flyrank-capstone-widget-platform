# app/services/notification_service.py
import logging
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Send a confirmation email after a submission.

    If sending fails, log the error but NEVER raise — the submission must succeed.
    """

    def send_submission_notification(
        self,
        owner_email: str,
        widget_name: str,
        submission_data: Dict[str, Any],
    ) -> bool:
        """Returns True if sent, False if failed. Never raises."""
        try:
            subject = f"New submission on '{widget_name}'"
            body_lines = [f"New submission received on widget '{widget_name}':\n"]
            for key, value in submission_data.items():
                body_lines.append(f"  {key}: {value}")
            body = "\n".join(body_lines)

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM
            msg["To"] = owner_email

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as server:
                server.send_message(msg)

            logger.info(f"Notification email sent to {owner_email} for widget '{widget_name}'")
            return True

        except Exception as e:
            # SAFE SIDE EFFECT: failure here must never block the submission
            logger.error(f"Failed to send notification email to {owner_email}: {e}")
            return False


notification_service = NotificationService()