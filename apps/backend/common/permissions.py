"""Autorização negada por padrão: cada endpoint declara o que permite.

A posse de um recurso é verificada no service, pelo escopo de cada domínio: recurso de
outro ator responde 404, sem revelar que existe.
"""

from rest_framework.permissions import BasePermission

from common.actor import actor_from_request


class DenyAll(BasePermission):
    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class IsPublic(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class IsAuthenticatedUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsActor(BasePermission):
    """Conta autenticada ou visitante com sessão válida."""

    def has_permission(self, request, view):
        return actor_from_request(request).is_identified
