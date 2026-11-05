"""Auxiliares de requisição."""

from __future__ import annotations

import hashlib
import hmac

from django.conf import settings


def client_ip(request) -> str:
    """IP real, considerando só os proxies confiáveis (`NUM_PROXIES`)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    remote = request.META.get("REMOTE_ADDR", "")
    if forwarded and settings.NUM_PROXIES > 0:
        hops = [hop.strip() for hop in forwarded.split(",") if hop.strip()]
        if hops:
            return hops[-min(settings.NUM_PROXIES, len(hops))]
    return remote


def hash_ip(ip: str) -> str:
    """IP nunca é guardado em claro: HMAC com a chave do projeto."""
    if not ip:
        return ""
    return hmac.new(settings.SECRET_KEY.encode(), ip.encode(), hashlib.sha256).hexdigest()


def request_id_of(request) -> str:
    return getattr(request, "request_id", "") or ""
