"""Códigos por e-mail: verificação e redefinição de senha.

Toda falha responde a mesma mensagem, para não revelar se a conta ou o código existem.
"""

from __future__ import annotations

import hmac
import secrets
from datetime import timedelta

import structlog
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from accounts.models import VerificationCode
from accounts.services.users import blacklist_all_tokens, validate_password_strength
from common.crypto import sha256_hex
from common.exceptions import CodeInvalid, GuardFailed
from notifications.services import send_email

User = get_user_model()
log = structlog.get_logger(__name__)

_MAX_ATTEMPTS = 5
_GENERIC_INVALID = "Código inválido ou expirado."


def _generate_code() -> str:
    return f"{secrets.randbelow(10**6):06d}"


def issue_code(*, user, kind: str, enforce_cooldown: bool = True) -> str:
    """Cria um código de uso único. O texto puro só sai por e-mail."""
    if enforce_cooldown:
        cooldown = settings.BUSINESS["ACCOUNT_CODE_RESEND_COOLDOWN_SECONDS"]
        latest = user.verification_codes.filter(kind=kind).order_by("-created_at").first()
        if latest and (timezone.now() - latest.created_at).total_seconds() < cooldown:
            raise GuardFailed("Aguarde para reenviar o código.", code="resend_too_soon")
    user.verification_codes.filter(kind=kind, state=VerificationCode.State.ISSUED).update(
        state=VerificationCode.State.EXPIRED
    )
    plaintext = _generate_code()
    VerificationCode.objects.create(
        user=user,
        kind=kind,
        code_hash=sha256_hex(plaintext),
        expires_at=timezone.now()
        + timedelta(minutes=settings.BUSINESS["ACCOUNT_CODE_TTL_MINUTES"]),
    )
    return plaintext


def validate_code(*, user, kind: str, submitted: str) -> None:
    code = (
        user.verification_codes.filter(kind=kind, state=VerificationCode.State.ISSUED)
        .order_by("-created_at")
        .first()
    )
    if code is None:
        raise CodeInvalid(_GENERIC_INVALID)
    if code.is_expired:
        code.state = VerificationCode.State.EXPIRED
        code.save(update_fields=["state", "updated_at"])
        raise CodeInvalid(_GENERIC_INVALID)
    if not hmac.compare_digest(code.code_hash, sha256_hex(submitted)):
        code.attempts += 1
        if code.attempts >= _MAX_ATTEMPTS:
            code.state = VerificationCode.State.FAILED
        code.save(update_fields=["attempts", "state", "updated_at"])
        raise CodeInvalid(_GENERIC_INVALID)
    code.state = VerificationCode.State.USED
    code.used_at = timezone.now()
    code.save(update_fields=["state", "used_at", "updated_at"])


def _send_code(*, user, plaintext: str, subject: str, template: str) -> None:
    send_email(
        to=user.email,
        subject=subject,
        template=template,
        context={
            "code": plaintext,
            "ttl_minutes": settings.BUSINESS["ACCOUNT_CODE_TTL_MINUTES"],
        },
    )


def request_email_verification(*, user, quiet_cooldown: bool = False) -> None:
    if user.email_verified:
        raise GuardFailed("E-mail já verificado.", code="already_verified")
    try:
        plaintext = issue_code(user=user, kind=VerificationCode.Kind.EMAIL_VERIFICATION)
    except GuardFailed:
        if quiet_cooldown:
            return
        raise
    _send_code(
        user=user,
        plaintext=plaintext,
        subject="Seu código de verificação da Kubo",
        template="verification_code",
    )


def confirm_email_verification(*, email: str, code: str):
    """Sem transação: os contadores de tentativa precisam sobreviver ao erro."""
    user = User.objects.filter(email=email.lower(), is_active=True).first()
    if user is None:
        raise CodeInvalid(_GENERIC_INVALID)
    validate_code(user=user, kind=VerificationCode.Kind.EMAIL_VERIFICATION, submitted=code)
    if not user.email_verified:
        user.email_verified = True
        user.save(update_fields=["email_verified", "updated_at"])
    return user


def request_password_reset(*, email: str) -> None:
    """Silencioso para e-mail desconhecido e dentro da espera: o endpoint sempre responde 200."""
    user = User.objects.filter(email=email.lower(), is_active=True).first()
    if user is None:
        return
    try:
        plaintext = issue_code(user=user, kind=VerificationCode.Kind.PASSWORD_RESET)
    except GuardFailed:
        return
    _send_code(
        user=user,
        plaintext=plaintext,
        subject="Redefinição de senha da Kubo",
        template="password_reset_code",
    )


def confirm_password_reset(*, email: str, code: str, new_password: str) -> None:
    """Possuir a caixa de e-mail também a comprova. Todas as sessões são encerradas."""
    user = User.objects.filter(email=email.lower(), is_active=True).first()
    if user is None:
        raise CodeInvalid(_GENERIC_INVALID)
    validate_password_strength(new_password, user=user)
    validate_code(user=user, kind=VerificationCode.Kind.PASSWORD_RESET, submitted=code)
    with transaction.atomic():
        user.set_password(new_password)
        user.email_verified = True
        user.save(update_fields=["password", "email_verified", "updated_at"])
        blacklist_all_tokens(user)
    log.info("password_reset_confirmed", user_id=str(user.globalid))
