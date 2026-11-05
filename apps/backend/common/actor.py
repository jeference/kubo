"""Quem está agindo: uma conta ou um visitante. Todo recurso do cliente pertence a um deles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import Q


@dataclass(frozen=True)
class Actor:
    user: Any = None
    visitor: Any = None

    @property
    def is_identified(self) -> bool:
        return self.user is not None or self.visitor is not None

    @property
    def key(self) -> str:
        """Identificador estável, usado em chaves de idempotência e de limite."""
        if self.user is not None:
            return f"u:{self.user.pk}"
        if self.visitor is not None:
            return f"v:{self.visitor.pk}"
        return ""

    def owner_filter(self) -> Q:
        """Filtro de posse para modelos com `user` e `visitor`."""
        if self.user is not None:
            return Q(user=self.user)
        if self.visitor is not None:
            return Q(visitor=self.visitor, user__isnull=True)
        return Q(pk__in=[])

    def creation_tasks_filter(self) -> Q:
        """Filtro de posse para tarefas de IA, pela criação."""
        if self.user is not None:
            return Q(creation__user=self.user)
        if self.visitor is not None:
            return Q(creation__visitor=self.visitor, creation__user__isnull=True)
        return Q(pk__in=[])

    def owner_fields(self) -> dict:
        if self.user is not None:
            return {"user": self.user, "visitor": None}
        return {"user": None, "visitor": self.visitor}


def actor_from_request(request) -> Actor:
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return Actor(user=user)
    visitor = getattr(request, "auth", None)
    if visitor is not None and visitor.__class__.__name__ == "Visitor":
        return Actor(visitor=visitor)
    return Actor()
