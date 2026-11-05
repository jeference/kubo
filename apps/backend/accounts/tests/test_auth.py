from __future__ import annotations

import re

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from accounts.authentication import VISITOR_COOKIE
from conftest import make_ready_creation
from integrations.adapters.email_console import outbox

User = get_user_model()
PASSWORD = "Senha-forte-123"


def _last_code() -> str:
    return re.search(r"\b(\d{6})\b", outbox[-1]["body"]).group(1)


def _register(anon, email="novo@exemplo.com"):
    return anon.post("/api/auth/register/", {"email": email, "password": PASSWORD})


def test_register_does_not_return_tokens_and_sends_code(anon):
    response = _register(anon)
    assert response.status_code == 201
    assert "tokens" not in response.data
    assert outbox[-1]["to"] == "novo@exemplo.com"
    assert "\n" in outbox[-1]["body"] or _last_code()


def test_register_duplicate_email(anon, user):
    response = _register(anon, email=user.email.upper())
    assert response.status_code == 422
    assert response.data["code"] == "email_taken"


def test_register_rejects_weak_password(anon):
    response = anon.post("/api/auth/register/", {"email": "a@b.com", "password": "12345678"})
    assert response.status_code == 422
    assert response.data["code"] == "weak_password"


def test_login_wrong_password_message_is_in_portuguese(anon, user):
    response = anon.post("/api/auth/login/", {"email": user.email, "password": "errada-123"})
    assert response.status_code == 401
    assert response.data["detail"] == "E-mail ou senha incorretos."


def test_validation_messages_are_in_portuguese(anon):
    response = anon.post("/api/auth/register/", {"email": "invalido", "password": "x"})
    assert response.status_code == 400
    assert "válido" in response.data["email"][0]


def test_login_unverified_is_blocked(anon):
    _register(anon)
    response = anon.post("/api/auth/login/", {"email": "novo@exemplo.com", "password": PASSWORD})
    assert response.status_code == 422
    assert response.data["code"] == "email_not_verified"


def test_verify_email_returns_tokens_and_marks_verified(anon):
    _register(anon)
    response = anon.post(
        "/api/auth/verify-email/", {"email": "novo@exemplo.com", "code": _last_code()}
    )
    assert response.status_code == 200
    assert response.data["tokens"]["access"]
    assert User.objects.get(email="novo@exemplo.com").email_verified


def test_verify_wrong_code_blocks_after_five_attempts(anon):
    _register(anon)
    code = _last_code()
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(5):
        response = anon.post(
            "/api/auth/verify-email/", {"email": "novo@exemplo.com", "code": wrong}
        )
        assert response.status_code == 422
    response = anon.post("/api/auth/verify-email/", {"email": "novo@exemplo.com", "code": code})
    assert response.status_code == 422


def test_login_and_refresh_rotation(anon, user):
    response = anon.post("/api/auth/login/", {"email": "CLIENTE@exemplo.com", "password": PASSWORD})
    assert response.status_code == 200
    refresh = response.data["refresh"]
    rotated = anon.post("/api/auth/refresh/", {"refresh": refresh})
    assert rotated.status_code == 200
    assert anon.post("/api/auth/refresh/", {"refresh": refresh}).status_code == 401


def test_logout_blacklists_refresh(anon, user):
    tokens = anon.post("/api/auth/login/", {"email": user.email, "password": PASSWORD}).data
    assert anon.post("/api/auth/logout/", {"refresh": tokens["refresh"]}).status_code == 205
    assert anon.post("/api/auth/refresh/", {"refresh": tokens["refresh"]}).status_code == 401


def test_password_reset_does_not_reveal_email(anon, user):
    unknown = anon.post("/api/auth/password/reset/", {"email": "ninguem@exemplo.com"})
    known = anon.post("/api/auth/password/reset/", {"email": user.email})
    assert unknown.status_code == known.status_code == 200
    assert unknown.data == known.data


def test_password_reset_changes_password_and_kills_sessions(anon, user):
    tokens = anon.post("/api/auth/login/", {"email": user.email, "password": PASSWORD}).data
    anon.post("/api/auth/password/reset/", {"email": user.email})
    response = anon.post(
        "/api/auth/password/reset/confirm/",
        {"email": user.email, "code": _last_code(), "new_password": "Outra-senha-456"},
    )
    assert response.status_code == 200
    assert anon.post("/api/auth/refresh/", {"refresh": tokens["refresh"]}).status_code == 401
    login = anon.post("/api/auth/login/", {"email": user.email, "password": "Outra-senha-456"})
    assert login.status_code == 200


def test_me_requires_account(anon, visitor_client, user_client):
    assert anon.get("/api/me/").status_code == 401
    assert visitor_client.get("/api/me/").status_code in (401, 403)
    assert user_client.get("/api/me/").status_code == 200


def test_me_patch_updates_profile(user_client):
    response = user_client.patch("/api/me/", {"first_name": "Ana", "phone": "11999998888"})
    assert response.status_code == 200
    assert response.data["first_name"] == "Ana"


def test_delete_account_anonymizes(user_client, user):
    make_ready_creation(user_client)
    wrong = user_client.post("/api/me/delete/", {"password": "errada"})
    assert wrong.status_code == 422
    response = user_client.post("/api/me/delete/", {"password": PASSWORD})
    assert response.status_code == 204
    user.refresh_from_db()
    assert not user.is_active
    assert user.email.endswith("@anonimizado.invalid")
    assert user.creations.filter(deleted_at__isnull=True).count() == 0


def test_visitor_create_returns_token_and_authenticates(anon):
    response = anon.post("/api/visitors/")
    assert response.status_code == 201
    client = APIClient(HTTP_X_KUBO_CLIENT="web")
    client.cookies[VISITOR_COOKIE] = response.data["token"]
    assert client.get("/api/quota/").status_code == 200


def test_visitor_write_requires_client_header(visitor_client):
    """Proteção contra CSRF: o cookie sozinho não autoriza escrita."""
    forged = APIClient()
    forged.cookies[VISITOR_COOKIE] = visitor_client.visitor_token
    response = forged.post("/api/creations/", {"text": "x", "style": "free"}, format="multipart")
    assert response.status_code in (401, 403)


def test_invalid_visitor_cookie_is_rejected():
    client = APIClient(HTTP_X_KUBO_CLIENT="web")
    client.cookies[VISITOR_COOKIE] = "token-invalido"
    assert client.get("/api/quota/").status_code in (401, 403)


@pytest.mark.parametrize("url", ["/api/creations/", "/api/cart/", "/api/orders/", "/api/quota/"])
def test_private_endpoints_require_actor(anon, url):
    assert anon.get(url).status_code in (401, 403)
