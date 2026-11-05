from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.services import auth_codes
from common.exceptions import GuardFailed
from common.serializers import GlobalIdSerializer

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=80, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True)


class UserSerializer(GlobalIdSerializer):
    roles = serializers.ListField(child=serializers.CharField(), read_only=True)
    first_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "email_verified", "roles", "first_name", "phone", "created_at"]
        read_only_fields = fields

    def _profile(self, user):
        return getattr(user, "profile", None)

    def get_first_name(self, user) -> str:
        profile = self._profile(user)
        return profile.first_name if profile else ""

    def get_phone(self, user) -> str:
        profile = self._profile(user)
        return profile.phone if profile else ""


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=80, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True)


class AccountDeleteSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class EmailVerifiedTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Credenciais válidas em conta não verificada não geram tokens: reenviamos o código."""

    default_error_messages = {"no_active_account": "E-mail ou senha incorretos."}

    def validate(self, attrs):
        attrs[self.username_field] = attrs[self.username_field].lower()
        data = super().validate(attrs)
        if not self.user.email_verified:
            auth_codes.request_email_verification(user=self.user, quiet_cooldown=True)
            raise GuardFailed(
                "Confirme seu e-mail para entrar. Enviamos um novo código.",
                code="email_not_verified",
            )
        return data


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)


class EmailOnlySerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class AccessRefreshSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)


class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RegisterResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    detail = serializers.CharField()


class AuthSessionResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    tokens = TokenPairSerializer()


class VisitorResponseSerializer(serializers.Serializer):
    token = serializers.CharField()


class ClaimResponseSerializer(serializers.Serializer):
    creations = serializers.IntegerField()
    orders = serializers.IntegerField()
