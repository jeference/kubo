from __future__ import annotations

from decimal import Decimal

from conftest import drain_worker
from creations.models import Creation, ProviderTask
from creations.quota import daily_spend_usd


def _create(client):
    return client.post("/api/creations/", {"text": "um gato", "style": "free"}, format="multipart")


def _business(settings, **overrides):
    settings.BUSINESS = {**settings.BUSINESS, **overrides}


def test_quota_is_debited_only_on_success(visitor_client):
    _create(visitor_client)
    usage = visitor_client.get("/api/quota/").data["image"]
    assert usage["used"] == 1  # reservada conta, para não passar do limite
    drain_worker()
    assert visitor_client.get("/api/quota/").data["image"] == {
        "limit": 10,
        "used": 1,
        "remaining": 9,
    }


def test_daily_limit_blocks(visitor_client, settings):
    _business(settings, QUOTA_PER_DAY={"image": 1, "edit": 15, "model": 6})
    assert _create(visitor_client).status_code == 202
    drain_worker()
    response = _create(visitor_client)
    assert response.status_code == 429
    assert response.data["code"] == "quota_exceeded"
    assert response.data["quota_kind"] == "image"


def test_ip_limit_applies_across_sessions(visitor_client, other_visitor_client, settings):
    _business(settings, QUOTA_PER_IP_PER_DAY={"image": 1, "edit": 60, "model": 24})
    assert _create(visitor_client).status_code == 202
    assert _create(other_visitor_client).status_code == 429


def test_active_task_limit(visitor_client, settings):
    _business(settings, MAX_ACTIVE_TASKS=1)
    assert _create(visitor_client).status_code == 202
    response = _create(visitor_client)
    assert response.status_code == 429
    assert response.data["code"] == "too_many_active_tasks"


def test_spend_cap_pauses_generation_but_not_catalog(visitor_client, settings):
    _business(settings, DAILY_SPEND_CAP_USD=0.01)
    creation = Creation.objects.create(style="free", visitor=visitor_client.visitor)
    ProviderTask.objects.create(
        creation=creation,
        kind=ProviderTask.Kind.TEXT_TO_IMAGE,
        status=ProviderTask.Status.SUCCEEDED,
        cost_usd=Decimal("0.05"),
    )
    assert daily_spend_usd() >= Decimal("0.05")
    response = _create(visitor_client)
    assert response.status_code == 503
    assert response.data["code"] == "generation_paused"
    assert visitor_client.get("/api/catalog/sizes/").status_code == 200
