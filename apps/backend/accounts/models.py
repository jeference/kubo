"""Identidade: conta (User) e visitante (Visitor).

Papéis são linhas em `Role`, a única fonte de autorização. Ser cliente não é papel: deriva
da posse de criações e pedidos. Não há tipos de conta separados nem painel administrativo.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

from common.models import BaseModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("E-mail é obrigatório.")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, BaseModel):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    anonymized_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = "email"

    def __str__(self) -> str:
        return f"User({self.globalid})"

    @property
    def roles(self) -> list[str]:
        return sorted(self.user_roles.values_list("name", flat=True))


class Role(BaseModel):
    class Name(models.TextChoices):
        STAFF = "staff", "Equipe"
        ADMIN = "admin", "Administrador"
        PARTNER_OWNER = "partner_owner", "Dono de parceiro"
        PARTNER_OPERATOR = "partner_operator", "Operador de parceiro"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    name = models.CharField(max_length=24, choices=Name.choices)

    class Meta(BaseModel.Meta):
        constraints = [models.UniqueConstraint(fields=["user", "name"], name="role_user_name_uq")]


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=32, blank=True)


class VerificationCode(BaseModel):
    """Código por e-mail: hash em repouso, uso único, validade e limite de tentativas."""

    class Kind(models.TextChoices):
        EMAIL_VERIFICATION = "email_verification", "Verificação de e-mail"
        PASSWORD_RESET = "password_reset", "Redefinição de senha"

    class State(models.TextChoices):
        ISSUED = "issued", "Emitido"
        USED = "used", "Usado"
        EXPIRED = "expired", "Expirado"
        FAILED = "failed", "Bloqueado por tentativas"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification_codes")
    kind = models.CharField(max_length=24, choices=Kind.choices)
    state = models.CharField(max_length=12, choices=State.choices, default=State.ISSUED)
    code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    used_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at


class Visitor(BaseModel):
    """Cliente sem conta. O token fica em cookie httpOnly; aqui, só o hash."""

    token_hash = models.CharField(max_length=64, unique=True)
    ip_hash = models.CharField(max_length=64, blank=True)
    last_seen_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="visitors"
    )
