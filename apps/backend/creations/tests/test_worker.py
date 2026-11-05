from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from common.alerts import alert
from conftest import drain_worker
from creations import glb, worker
from creations.models import Creation, ProviderTask, QuotaReservation
from integrations import ports
from integrations.adapters.stubs import build_sample_glb
from integrations.ports import Model3DStatus


def _create(client, text="um gato"):
    return client.post("/api/creations/", {"text": text, "style": "free"}, format="multipart")


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


def test_model_without_texture_is_retried_then_fails(visitor_client, monkeypatch):
    creation_id = _create(visitor_client).data["id"]
    drain_worker()
    visitor_client.post(f"/api/creations/{creation_id}/approve/")

    class Grey:
        provider = "stub"
        model_name = "stub-3d"

        def submit(self, *, image):
            return "cinza"

        def get(self, *, external_id):
            return Model3DStatus(status="success", file_bytes=build_sample_glb(with_texture=False))

    monkeypatch.setattr("creations.worker.get_model_3d_port", lambda: Grey())
    drain_worker()
    detail = visitor_client.get(f"/api/creations/{creation_id}/").data
    assert detail["status"] == "model_failed"
    assert detail["error"]["code"] == "model_without_texture"
    assert detail["model"] is None
    reservation = QuotaReservation.objects.get(task__kind=ProviderTask.Kind.IMAGE_TO_MODEL)
    assert reservation.state == QuotaReservation.State.RELEASED


def test_model_timeout_fails(visitor_client, settings):
    creation_id = _create(visitor_client).data["id"]
    drain_worker()
    visitor_client.post(f"/api/creations/{creation_id}/approve/")
    settings.STUB_MODEL_SECONDS = 9999
    drain_worker(max_rounds=1)
    ProviderTask.objects.filter(kind=ProviderTask.Kind.IMAGE_TO_MODEL).update(
        started_at=timezone.now() - timedelta(hours=1), next_attempt_at=None
    )
    assert worker.run_once()
    detail = visitor_client.get(f"/api/creations/{creation_id}/").data
    assert detail["status"] == "model_failed"
    assert detail["error"]["code"] == "timeout"


def test_reconcile_stuck_tasks(visitor_client):
    creation_id = _create(visitor_client).data["id"]
    ProviderTask.objects.update(
        status=ProviderTask.Status.RUNNING, started_at=timezone.now() - timedelta(days=1)
    )
    assert worker.reconcile_stuck_tasks() == 1
    assert Creation.objects.get(globalid=creation_id).status == Creation.Status.IMAGE_FAILED


def test_glb_helpers():
    textured = build_sample_glb()
    assert glb.has_texture(textured)
    assert glb.triangle_count(textured) > 0
    assert not glb.has_texture(build_sample_glb(with_texture=False))
    assert not glb.has_texture(b"lixo")


def test_ports_resolve_stubs():
    assert ports.get_image_generation_port().provider == "stub"


def test_alert_does_not_raise():
    alert("teste", valor=1)
