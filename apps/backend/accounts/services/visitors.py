from __future__ import annotations

import secrets

from django.db import transaction

from accounts.models import Visitor
from common.crypto import sha256_hex
from common.exceptions import GuardFailed


def create_visitor(*, ip_hash: str = "") -> tuple[Visitor, str]:
    """Retorna o visitante e o token em texto puro, que só existe no cookie."""
    token = secrets.token_urlsafe(32)
    visitor = Visitor.objects.create(token_hash=sha256_hex(token), ip_hash=ip_hash)
    return visitor, token


def claim_visitor(*, user, visitor: Visitor | None) -> dict:
    """Transfere para a conta o que o visitante criou e os pedidos do e-mail verificado.

    Idempotente. Pedidos antigos só vêm com e-mail verificado: ele prova a posse do endereço.
    """
    from creations.services import transfer_visitor_creations
    from orders.services import claim_orders_for_user, transfer_visitor_cart

    if not user.email_verified:
        raise GuardFailed("Confirme seu e-mail primeiro.", code="email_not_verified")
    creations = 0
    with transaction.atomic():
        if visitor is not None and (visitor.user_id is None or visitor.user_id == user.pk):
            creations = transfer_visitor_creations(visitor=visitor, user=user)
            transfer_visitor_cart(visitor=visitor, user=user)
            if visitor.user_id is None:
                visitor.user = user
                visitor.save(update_fields=["user", "updated_at"])
        orders = claim_orders_for_user(user=user, visitor=visitor)
    return {"creations": creations, "orders": orders}
