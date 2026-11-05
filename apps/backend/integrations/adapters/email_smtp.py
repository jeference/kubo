from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from integrations.ports import EmailPort


class SmtpEmailAdapter(EmailPort):
    def send(self, *, to: str, subject: str, body: str, html_body: str | None = None) -> None:
        message = EmailMultiAlternatives(
            subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, to=[to]
        )
        if html_body:
            message.attach_alternative(html_body, "text/html")
        message.send(fail_silently=False)
