"""Views finas sobre os services e o SimpleJWT."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts import serializers as s
from accounts.authentication import visitor_from_cookie
from accounts.services import auth_codes, users, visitors
from common.exceptions import GuardFailed
from common.http import client_ip, hash_ip
from common.permissions import IsAuthenticatedUser, IsPublic
from common.serializers import DetailResponseSerializer
from common.throttling import EmailScopedRateThrottle

User = get_user_model()


def _tokens_for(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class VisitorCreateView(APIView):
    """Chamado pelo BFF, que grava o token em cookie httpOnly."""

    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "visitor_create"

    @extend_schema(request=None, responses={201: s.VisitorResponseSerializer}, auth=[])
    def post(self, request):
        _, token = visitors.create_visitor(ip_hash=hash_ip(client_ip(request)))
        return Response(
            s.VisitorResponseSerializer({"token": token}).data, status=status.HTTP_201_CREATED
        )


class RegisterView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_register"

    @extend_schema(request=s.RegisterSerializer, responses={201: s.RegisterResponseSerializer})
    def post(self, request):
        data = s.RegisterSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        user = users.register_user(**data.validated_data)
        out = s.RegisterResponseSerializer(
            {"user": user, "detail": "Enviamos um código de verificação para o seu e-mail."}
        )
        return Response(out.data, status=status.HTTP_201_CREATED)


@extend_schema(request=s.LoginSerializer, responses=s.TokenPairSerializer)
class LoginView(TokenObtainPairView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    serializer_class = s.EmailVerifiedTokenObtainPairSerializer
    throttle_classes = [ScopedRateThrottle, EmailScopedRateThrottle]
    throttle_scope = "auth_login"
    email_throttle_scope = "auth_login_email"


@extend_schema(request=s.RefreshTokenRequestSerializer, responses=s.AccessRefreshSerializer)
class RefreshView(TokenRefreshView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_refresh"


class VerifyEmailView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle, EmailScopedRateThrottle]
    throttle_scope = "auth_verify"
    email_throttle_scope = "auth_verify_email"

    @extend_schema(request=s.VerifyEmailSerializer, responses=s.AuthSessionResponseSerializer)
    def post(self, request):
        data = s.VerifyEmailSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        user = auth_codes.confirm_email_verification(**data.validated_data)
        out = s.AuthSessionResponseSerializer({"user": user, "tokens": _tokens_for(user)})
        return Response(out.data)


class ResendVerificationView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle, EmailScopedRateThrottle]
    throttle_scope = "auth_resend"
    email_throttle_scope = "auth_resend_email"

    @extend_schema(request=s.EmailOnlySerializer, responses=DetailResponseSerializer)
    def post(self, request):
        data = s.EmailOnlySerializer(data=request.data)
        data.is_valid(raise_exception=True)
        user = User.objects.filter(
            email=data.validated_data["email"].lower(), is_active=True
        ).first()
        if user is not None:
            try:
                auth_codes.request_email_verification(user=user)
            except GuardFailed:
                pass
        return Response(
            DetailResponseSerializer(
                {"detail": "Se o e-mail existir e não estiver verificado, enviaremos um código."}
            ).data
        )


class LogoutView(APIView):
    """O refresh token é a própria credencial: funciona mesmo com o access vencido."""

    authentication_classes: list = []
    permission_classes = [IsPublic]

    @extend_schema(request=s.RefreshTokenRequestSerializer, responses={205: None})
    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            raise GuardFailed("Refresh token obrigatório.", code="refresh_required")
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            pass
        return Response(status=status.HTTP_205_RESET_CONTENT)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(request=s.PasswordChangeSerializer, responses=DetailResponseSerializer)
    def post(self, request):
        data = s.PasswordChangeSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        users.change_password(user=request.user, **data.validated_data)
        return Response(DetailResponseSerializer({"detail": "Senha alterada."}).data)


class PasswordResetView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle, EmailScopedRateThrottle]
    throttle_scope = "auth_password_reset"
    email_throttle_scope = "auth_password_reset_email"

    @extend_schema(request=s.EmailOnlySerializer, responses=DetailResponseSerializer)
    def post(self, request):
        data = s.EmailOnlySerializer(data=request.data)
        data.is_valid(raise_exception=True)
        auth_codes.request_password_reset(email=data.validated_data["email"])
        return Response(
            DetailResponseSerializer({"detail": "Se o e-mail existir, enviaremos um código."}).data
        )


class PasswordResetConfirmView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle, EmailScopedRateThrottle]
    throttle_scope = "auth_password_reset_confirm"
    email_throttle_scope = "auth_password_reset_confirm_email"

    @extend_schema(request=s.PasswordResetConfirmSerializer, responses=DetailResponseSerializer)
    def post(self, request):
        data = s.PasswordResetConfirmSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        auth_codes.confirm_password_reset(**data.validated_data)
        return Response(DetailResponseSerializer({"detail": "Senha redefinida."}).data)


class MeView(APIView):
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(responses=s.UserSerializer)
    def get(self, request):
        return Response(s.UserSerializer(request.user).data)

    @extend_schema(request=s.ProfileUpdateSerializer, responses=s.UserSerializer)
    def patch(self, request):
        data = s.ProfileUpdateSerializer(data=request.data, partial=True)
        data.is_valid(raise_exception=True)
        users.update_profile(user=request.user, **data.validated_data)
        user = User.objects.select_related("profile").get(pk=request.user.pk)
        return Response(s.UserSerializer(user).data)


class AccountDeleteView(APIView):
    """POST, porque precisa da senha no corpo."""

    permission_classes = [IsAuthenticatedUser]

    @extend_schema(request=s.AccountDeleteSerializer, responses={204: None})
    def post(self, request):
        data = s.AccountDeleteSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        users.delete_account(user=request.user, password=data.validated_data["password"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClaimView(APIView):
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(request=None, responses=s.ClaimResponseSerializer)
    def post(self, request):
        result = visitors.claim_visitor(user=request.user, visitor=visitor_from_cookie(request))
        return Response(s.ClaimResponseSerializer(result).data)
