"""Testes: sempre com stubs, sem rede. Rode com o Postgres local (`make db`)."""

from __future__ import annotations

import io

import pytest
from django.core.cache import cache
from PIL import Image
from rest_framework.test import APIClient

from integrations.adapters import email_console
from integrations.ports import reset_ports

STUBS = "integrations.adapters.stubs"


@pytest.fixture(autouse=True)
def _offline_settings(settings, tmp_path, db):
    settings.IMAGE_GENERATION_ADAPTER = f"{STUBS}.StubImageGenerationAdapter"
    settings.PAYMENT_GATEWAY_ADAPTER = f"{STUBS}.StubPaymentGatewayAdapter"
    settings.SHIPPING_ADAPTER = f"{STUBS}.StubShippingAdapter"
    settings.ADDRESS_LOOKUP_ADAPTER = f"{STUBS}.StubAddressLookupAdapter"
    settings.MEDIA_STORAGE_ADAPTER = "integrations.adapters.media_local.LocalMediaAdapter"
    settings.EMAIL_ADAPTER = "integrations.adapters.email_console.ConsoleEmailAdapter"
    settings.MEDIA_ROOT = str(tmp_path / "media")
    settings.STUB_IMAGE_SECONDS = 0
    settings.ABACATE_PAY_WEBHOOK_SECRET = "segredo-teste"
    settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    cache.clear()
    reset_ports()
    email_console.outbox.clear()
    yield
    reset_ports()


@pytest.fixture
def anon():
    return APIClient()


def client_for_visitor():
    from accounts.authentication import VISITOR_COOKIE
    from accounts.services.visitors import create_visitor

    visitor, token = create_visitor(ip_hash="iphash")
    client = APIClient(HTTP_X_KUBO_CLIENT="web")
    client.cookies[VISITOR_COOKIE] = token
    client.visitor = visitor
    client.visitor_token = token
    return client


@pytest.fixture
def visitor_client():
    return client_for_visitor()


@pytest.fixture
def other_visitor_client():
    return client_for_visitor()


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model

    return get_user_model().objects.create_user(
        email="cliente@exemplo.com", password="Senha-forte-123", email_verified=True
    )


@pytest.fixture
def user_client(user):
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient(HTTP_X_KUBO_CLIENT="web")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}",
        HTTP_X_KUBO_CLIENT="web",
    )
    client.user = user
    return client


def drain_worker(max_rounds: int = 20) -> None:
    from creations import worker
    from creations.models import ProviderTask

    for _ in range(max_rounds):
        ProviderTask.objects.filter(next_attempt_at__isnull=False).update(next_attempt_at=None)
        if not worker.run_once():
            return


def photo_upload():
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), "white").save(buffer, format="PNG")
    buffer.seek(0)
    buffer.name = "foto.png"
    return buffer


def creation_payload(text="um dragão azul", **fields):
    """Corpo de `POST /api/creations/`: foto e o pedido de alteração."""
    return {
        "text": text,
        "style": "free",
        "photo": photo_upload(),
        **fields,
    }


def make_ready_creation(client, text="um dragão azul"):
    """Criação pronta para comprar, passando pela API e pelo worker."""
    response = client.post("/api/creations/", creation_payload(text), format="multipart")
    assert response.status_code == 202, response.data
    creation_id = response.data["id"]
    drain_worker()
    detail = client.get(f"/api/creations/{creation_id}/")
    assert detail.data["status"] == "ready", detail.data
    return detail.data
