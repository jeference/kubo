"""Limites por e-mail, somados aos limites por IP: trocar de IP não burla o limite da conta."""

from __future__ import annotations

import hashlib

from rest_framework.throttling import ScopedRateThrottle


class EmailScopedRateThrottle(ScopedRateThrottle):
    scope_attr = "email_throttle_scope"

    def get_cache_key(self, request, view):
        email = str(request.data.get("email", "")).strip().lower()
        if not email:
            return None
        ident = hashlib.sha256(email.encode()).hexdigest()
        return self.cache_format % {"scope": self.scope, "ident": ident}
