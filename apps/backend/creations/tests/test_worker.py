from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from common.alerts import alert
from conftest import creation_payload
from creations import worker
from creations.models import Creation, ProviderTask
from integrations import ports


def _create(client, text="um gato"):
    return client.post("/api/creations/", creation_payload(text), format="multipart")


def test_claim_skips_locked_and_future_tasks(visitor_client):
    _create(visitor_client)
    task = ProviderTask.objects.get()
    task.next_attempt_at = timezone.now() + timedelta(hours=1)
    task.save()
    assert worker.claim_task() is None
    task.next_attempt_at = None
    task.locked_until = timezone.now() + timedelta(hours=1)
    task.save()
    assert worker.claim_task() is None


def test_expired_lease_is_reclaimed(visitor_client):
    _create(visitor_client)
    task = worker.claim_task()
    assert task is not None
    ProviderTask.objects.filter(pk=task.pk).update(
        locked_until=timezone.now() - timedelta(seconds=1)
    )
    assert worker.claim_task().pk == task.pk


def test_reconcile_stuck_tasks(visitor_client):
    creation_id = _create(visitor_client).data["id"]
    ProviderTask.objects.update(
        status=ProviderTask.Status.RUNNING, started_at=timezone.now() - timedelta(days=1)
    )
    assert worker.reconcile_stuck_tasks() == 1
    assert Creation.objects.get(globalid=creation_id).status == Creation.Status.IMAGE_FAILED


def test_ports_resolve_stubs():
    assert ports.get_image_generation_port().provider == "stub"


def test_alert_does_not_raise():
    alert("teste", valor=1)
