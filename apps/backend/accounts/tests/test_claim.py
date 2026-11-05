from __future__ import annotations

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.authentication import VISITOR_COOKIE
from conftest import make_ready_creation
from orders.tests.helpers import place_order


def _logged_in_with_cookie(user, visitor_client):
    client = APIClient(HTTP_X_KUBO_CLIENT="web")
    client.cookies[VISITOR_COOKIE] = visitor_client.visitor_token
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}",
        HTTP_X_KUBO_CLIENT="web",
    )
    return client


def test_claim_moves_creations_and_cart(user, visitor_client):
    creation = make_ready_creation(visitor_client)
    size = visitor_client.get("/api/catalog/sizes/").data[0]
    visitor_client.post(
        "/api/cart/items/", {"creation_id": creation["id"], "size_id": size["id"], "quantity": 1}
    )
    client = _logged_in_with_cookie(user, visitor_client)
    response = client.post("/api/me/claim/")
    assert response.status_code == 200
    assert response.data["creations"] == 1
    assert client.get(f"/api/creations/{creation['id']}/").status_code == 200
    assert client.get("/api/cart/").data["item_count"] == 1
    assert visitor_client.get(f"/api/creations/{creation['id']}/").status_code == 404


def test_claim_is_idempotent(user, visitor_client):
    make_ready_creation(visitor_client)
    client = _logged_in_with_cookie(user, visitor_client)
    assert client.post("/api/me/claim/").data["creations"] == 1
    assert client.post("/api/me/claim/").data["creations"] == 0


def test_claim_links_orders_only_for_matching_verified_email(user, visitor_client):
    mine = place_order(visitor_client, email=user.email)
    other = place_order(visitor_client, email="outra-pessoa@exemplo.com")
    client = _logged_in_with_cookie(user, visitor_client)
    assert client.post("/api/me/claim/").data["orders"] == 1
    assert client.get(f"/api/orders/{mine['id']}/").status_code == 200
    assert client.get(f"/api/orders/{other['id']}/").status_code == 404


def test_claim_requires_verified_email(db):
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_user(email="x@exemplo.com", password="Senha-forte-123")
    client = APIClient(HTTP_X_KUBO_CLIENT="web")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")
    response = client.post("/api/me/claim/")
    assert response.status_code == 422
    assert response.data["code"] == "email_not_verified"
