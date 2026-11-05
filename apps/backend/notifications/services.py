"""E-mail transacional: síncrono, melhor esforço. Falha não desfaz o que já aconteceu.

Chame de dentro de `transaction.on_commit` quando o envio depender de uma transação.
"""

from __future__ import annotations

import structlog
from django.conf import settings
from django.template.loader import render_to_string

from common.alerts import alert
from common.crypto import sha256_hex
from integrations.ports import get_email_port
from notifications.models import EmailLog

log = structlog.get_logger(__name__)


def send_email(*, to: str, subject: str, template: str, context: dict) -> bool:
    full_context = {**context, "app_url": settings.CONSUMER_APP_URL, "subject": subject}
    body = render_to_string(f"emails/{template}.txt", full_context)
    html = render_to_string(f"emails/{template}.html", full_context)
    to_hash = sha256_hex(to.lower())
    try:
        get_email_port().send(to=to, subject=subject, body=body, html_body=html)
    except Exception as exc:
        EmailLog.objects.create(
            to_hash=to_hash, template=template, status=EmailLog.Status.FAILED, error=str(exc)[:500]
        )
        alert("email_failed", template=template, error=str(exc)[:200])
        return False
    EmailLog.objects.create(to_hash=to_hash, template=template, status=EmailLog.Status.SENT)
    return True
