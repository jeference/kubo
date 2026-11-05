from django.urls import path

from accounts import views

urlpatterns = [
    path("visitors/", views.VisitorCreateView.as_view(), name="visitor-create"),
    path("auth/register/", views.RegisterView.as_view(), name="auth-register"),
    path("auth/login/", views.LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", views.RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("auth/verify-email/", views.VerifyEmailView.as_view(), name="auth-verify-email"),
    path(
        "auth/verify-email/resend/",
        views.ResendVerificationView.as_view(),
        name="auth-verify-email-resend",
    ),
    path("auth/password/change/", views.PasswordChangeView.as_view(), name="auth-password-change"),
    path("auth/password/reset/", views.PasswordResetView.as_view(), name="auth-password-reset"),
    path(
        "auth/password/reset/confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="auth-password-reset-confirm",
    ),
    path("me/", views.MeView.as_view(), name="me"),
    path("me/claim/", views.ClaimView.as_view(), name="me-claim"),
    path("me/delete/", views.AccountDeleteView.as_view(), name="me-delete"),
]
