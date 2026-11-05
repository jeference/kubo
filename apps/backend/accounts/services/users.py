"""Serviços de conta. Lógica aqui; as views só orquestram."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile, Role
from common.exceptions import GuardFailed

User = get_user_model()


def validate_password_strength(password: str, *, user=None) -> None:
    try:
        validate_password(password, user=user)
    except ValidationError as exc:
        raise GuardFailed(" ".join(exc.messages), code="weak_password")


def grant_role(*, user, name: str) -> None:
    Role.objects.get_or_create(user=user, name=name)


@transaction.atomic
def register_user(*, email: str, password: str, first_name: str = "", phone: str = ""):
    from accounts.services import auth_codes

    email = email.lower()
    if User.objects.filter(email=email).exists():
        raise GuardFailed("E-mail já cadastrado.", code="email_taken")
    validate_password_strength(password, user=User(email=email))
    user = User.objects.create_user(email=email, password=password)
    Profile.objects.create(user=user, first_name=first_name, phone=phone)
    auth_codes.request_email_verification(user=user)
    return user


def change_password(*, user, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise GuardFailed("Senha atual incorreta.", code="wrong_password")
    validate_password_strength(new_password, user=user)
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])


def update_profile(*, user, first_name: str | None = None, phone: str | None = None):
    profile, _ = Profile.objects.get_or_create(user=user)
    if first_name is not None:
        profile.first_name = first_name
    if phone is not None:
        profile.phone = phone
    profile.save()
    return profile


def blacklist_all_tokens(user) -> None:
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


@transaction.atomic
def delete_account(*, user, password: str) -> None:
    """Exclusão a pedido: anonimiza a conta e aplica a retenção às criações sem pedido.

    Pedidos ficam guardados pelas obrigações fiscais. Pedido em aberto impede a exclusão,
    porque ainda precisamos dos dados para entregar.
    """
    from creations import services as creation_services
    from orders import services as order_services

    if not user.check_password(password):
        raise GuardFailed("Senha incorreta.", code="wrong_password")
    if order_services.has_open_orders(user):
        raise GuardFailed(
            "Você tem pedidos em andamento. Aguarde a entrega para excluir a conta.",
            code="open_orders",
        )
    creation_services.delete_all_for_user(user)
    order_services.delete_saved_addresses(user)
    Profile.objects.filter(user=user).delete()
    blacklist_all_tokens(user)
    user.email = f"excluido-{user.globalid}@anonimizado.invalid"
    user.email_verified = False
    user.is_active = False
    user.anonymized_at = timezone.now()
    user.set_unusable_password()
    user.save()
