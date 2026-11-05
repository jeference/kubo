"""Autenticação do visitante, por cookie httpOnly.

O cookie autentica sozinho, então escritas exigem também o cabeçalho `X-Kubo-Client`, que um
formulário de outro site não consegue enviar (proteção contra CSRF, junto de SameSite=Lax).
"""

from __future__ import annotations

from datetime import timedelta

import structlog
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication

from accounts.models import Visitor
from common.crypto import sha256_hex

VISITOR_COOKIE = "kubo_visitor"
CLIENT_HEADER = "HTTP_X_KUBO_CLIENT"
_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
_LAST_SEEN_RESOLUTION = timedelta(hours=1)


def visitor_from_cookie(request) -> Visitor | None:
    token = request.COOKIES.get(VISITOR_COOKIE)
    if not token:
        return None
    return Visitor.objects.filter(token_hash=sha256_hex(token)).first()


class VisitorAuthentication(BaseAuthentication):
    def authenticate(self, request):
        visitor = visitor_from_cookie(request)
        if visitor is None:
            return None
        if request.method not in _SAFE_METHODS and not request.META.get(CLIENT_HEADER):
            return None
        now = timezone.now()
        if now - visitor.last_seen_at > _LAST_SEEN_RESOLUTION:
            Visitor.objects.filter(pk=visitor.pk).update(last_seen_at=now)
        structlog.contextvars.bind_contextvars(visitor_id=str(visitor.globalid))
        return AnonymousUser(), visitor


class VisitorAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "accounts.authentication.VisitorAuthentication"
    name = "visitorCookie"

    def get_security_definition(self, auto_schema):
        return {"type": "apiKey", "in": "cookie", "name": VISITOR_COOKIE}
