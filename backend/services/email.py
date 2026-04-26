import logging
from html import escape
from urllib.parse import urlencode
from urllib.parse import urlparse

import resend

from core.config import settings


logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


def _get_configured_sender() -> str:
    return settings.email_from


def _is_local_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.hostname in {"localhost", "127.0.0.1"}


def _allow_dev_fallback() -> bool:
    if settings.email_dev_fallback is not None:
        return settings.email_dev_fallback

    return _is_local_url(settings.frontend_url) and _is_local_url(settings.backend_base_url)


def email_delivery_enabled() -> bool:
    return bool(settings.resend_api_key) or _allow_dev_fallback()


def _send_email(*, to: str, subject: str, html: str) -> None:
    if not settings.resend_api_key:
        if not _allow_dev_fallback():
            raise EmailDeliveryError("Email delivery is not configured")

        print(f"[email-dev-fallback] To: {to}")
        print(f"[email-dev-fallback] Subject: {subject}")
        print(html)
        return

    try:
        resend.api_key = settings.resend_api_key
        resend.Emails.send(
            {
                "from": _get_configured_sender(),
                "to": [to],
                "subject": subject,
                "html": html,
            }
        )
    except Exception as exc:
        if _allow_dev_fallback():
            print(f"[email-dev-fallback] Delivery failed: {exc}")
            print(f"[email-dev-fallback] To: {to}")
            print(f"[email-dev-fallback] Subject: {subject}")
            print(html)
            return

        logger.exception("Email delivery failed for subject '%s'", subject)
        raise EmailDeliveryError("Email delivery failed") from exc


def send_signup_otp_email(*, recipient_email: str, recipient_name: str, otp_code: str) -> None:
    safe_name = escape(recipient_name)
    html = f"""
    <div>
      <h2>Your lebooks verification code</h2>
      <p>Hi {safe_name},</p>
      <p>Use this code to finish creating your lebooks account:</p>
      <p style="font-size: 28px; font-weight: 700; letter-spacing: 6px;">{otp_code}</p>
      <p>This code expires in 10 minutes.</p>
      <p>If you did not request this code, you can ignore this email.</p>
    </div>
    """

    _send_email(
        to=recipient_email,
        subject="Your lebooks verification code",
        html=html,
    )


def send_password_reset_email(*, recipient_email: str, recipient_name: str, token: str) -> None:
    reset_query = urlencode({"token": token})
    reset_link = f"{settings.frontend_url.rstrip('/')}/reset-password?{reset_query}"
    safe_name = escape(recipient_name)

    html = f"""
    <div>
      <h2>Reset your lebooks password</h2>
      <p>Hi {safe_name},</p>
      <p>We received a request to reset your password. Click below to choose a new one.</p>
      <p><a href="{reset_link}">Reset password</a></p>
      <p>If you did not request this, you can ignore this email.</p>
    </div>
    """

    _send_email(
        to=recipient_email,
        subject="Reset your lebooks password",
        html=html,
    )
