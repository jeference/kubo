from __future__ import annotations

import io

from PIL import Image

from conftest import drain_worker, make_ready_creation
from creations.models import Creation, ProviderTask, QuotaReservation


def _photo():
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), "white").save(buffer, format="PNG")
    buffer.seek(0)
    buffer.name = "foto.png"
    return buffer


def _create(client, **fields):
    payload = {"text": "um gato", "style": "free", **fields}
    return client.post("/api/creations/", payload, format="multipart")


def test_create_from_text_goes_to_approval(visitor_client):
    response = _create(visitor_client)
    assert response.status_code == 202
    assert response.data["status"] == "generating_image"
    assert response.data["is_generating"] is True
    drain_worker()
    detail = visitor_client.get(f"/api/creations/{response.data['id']}/").data
    assert detail["status"] == "awaiting_approval"
    assert len(detail["versions"]) == 1
    assert detail["versions"][0]["image_url"]
    assert detail["current_version_id"] == detail["versions"][0]["id"]
    task = ProviderTask.objects.get(creation__globalid=response.data["id"])
    assert task.rendered_prompt and task.prompt_version
    assert task.status == ProviderTask.Status.SUCCEEDED


def test_create_requires_text_or_photo(visitor_client):
    response = visitor_client.post(
        "/api/creations/", {"text": " ", "style": "free"}, format="multipart"
    )
    assert response.status_code == 422
    assert response.data["code"] == "empty_input"


def test_invalid_style(visitor_client):
    response = _create(visitor_client, style="inexistente")
    assert response.data["code"] == "invalid_style"


def test_photo_requires_rights_declaration(visitor_client):
    response = _create(visitor_client, photo=_photo())
    assert response.status_code == 422
    assert response.data["code"] == "rights_required"


def test_photo_flow(visitor_client):
    response = _create(visitor_client, photo=_photo(), rights_accepted=True, text="")
    assert response.status_code == 202, response.data
    assert response.data["has_photo"] is True
    drain_worker()
    detail = visitor_client.get(f"/api/creations/{response.data['id']}/").data
    assert detail["status"] == "awaiting_approval"
    assert detail["versions"][0]["origin"] == "photo"
    creation = Creation.objects.get(globalid=response.data["id"])
    assert creation.input.rights_accepted_at is not None


def test_other_visitor_cannot_see_or_act(visitor_client, other_visitor_client, user_client):
    creation_id = _create(visitor_client).data["id"]
    for client in (other_visitor_client, user_client):
        assert client.get(f"/api/creations/{creation_id}/").status_code == 404
        assert client.post(f"/api/creations/{creation_id}/approve/").status_code == 404
        assert client.delete(f"/api/creations/{creation_id}/").status_code == 404
    assert other_visitor_client.get("/api/creations/").data["count"] == 0


def test_list_is_scoped_and_paginated(visitor_client):
    _create(visitor_client)
    data = visitor_client.get("/api/creations/").data
    assert data["count"] == 1
    assert data["results"][0]["status"] == "generating_image"


def test_full_flow_reaches_ready_with_model_and_estimates(visitor_client):
    detail = make_ready_creation(visitor_client)
    assert detail["model"]["glb_url"]
    assert detail["model"]["triangles"] > 0
    assert detail["blocked_size_ids"] == []
    creation = Creation.objects.get(globalid=detail["id"])
    assert creation.current_model.estimate_method == "voxel_flood"
    assert creation.current_model.cost_estimates.count() == 5


def test_approve_before_image_is_illegal(visitor_client):
    creation_id = _create(visitor_client).data["id"]
    response = visitor_client.post(f"/api/creations/{creation_id}/approve/")
    assert response.status_code in (409, 422)


def test_content_refusal_shows_message_and_releases_quota(visitor_client):
    creation_id = _create(visitor_client, text="__recusar__").data["id"]
    drain_worker()
    detail = visitor_client.get(f"/api/creations/{creation_id}/").data
    assert detail["status"] == "image_failed"
    assert detail["error"]["code"] == "content_refused"
    assert "regras de conteúdo" in detail["error"]["message"]
    reservation = QuotaReservation.objects.get(task__creation__globalid=creation_id)
    assert reservation.state == QuotaReservation.State.RELEASED
    assert visitor_client.get("/api/quota/").data["image"]["used"] == 0


def test_provider_failure_retries_then_fails_and_user_can_retry(visitor_client):
    creation_id = _create(visitor_client, text="__falhar__").data["id"]
    drain_worker()
    task = ProviderTask.objects.get(creation__globalid=creation_id)
    assert task.attempts == 3
    assert task.status == ProviderTask.Status.FAILED
    detail = visitor_client.get(f"/api/creations/{creation_id}/").data
    assert detail["status"] == "image_failed"
    response = visitor_client.post(f"/api/creations/{creation_id}/retry/")
    assert response.status_code == 202
    assert response.data["status"] == "generating_image"
    assert response.data["error"] is None


def test_edit_creates_version_and_apply_discards_model(visitor_client):
    detail = make_ready_creation(visitor_client)
    first_version = detail["versions"][0]["id"]
    response = visitor_client.post(
        f"/api/creations/{detail['id']}/edits/",
        {"version_id": first_version, "instruction": "capa vermelha"},
    )
    assert response.status_code == 202
    assert response.data["edit_tasks"][0]["is_active"] is True
    drain_worker()
    edited = visitor_client.get(f"/api/creations/{detail['id']}/").data
    assert len(edited["versions"]) == 2
    assert edited["versions"][1]["parent_id"] == first_version
    assert edited["status"] == "ready"
    assert edited["current_version_id"] == first_version

    applied = visitor_client.post(
        f"/api/creations/{detail['id']}/apply-version/",
        {"version_id": edited["versions"][1]["id"]},
    ).data
    assert applied["status"] == "awaiting_approval"
    assert applied["model"] is None
    assert applied["current_version_id"] == edited["versions"][1]["id"]
    creation = Creation.objects.get(globalid=detail["id"])
    assert creation.models_3d.get().discarded_at is not None


def test_back_and_reapprove_reuses_model_without_new_quota(visitor_client):
    detail = make_ready_creation(visitor_client)
    assert visitor_client.get("/api/quota/").data["model"]["used"] == 1
    back = visitor_client.post(f"/api/creations/{detail['id']}/back/").data
    assert back["status"] == "awaiting_approval"
    assert back["model"] is not None
    again = visitor_client.post(f"/api/creations/{detail['id']}/approve/").data
    assert again["status"] == "ready"
    assert visitor_client.get("/api/quota/").data["model"]["used"] == 1


def test_edit_validations(visitor_client):
    detail = make_ready_creation(visitor_client)
    version = detail["versions"][0]["id"]
    url = f"/api/creations/{detail['id']}/edits/"
    assert visitor_client.post(url, {"version_id": version, "instruction": " "}).status_code == 400
    too_long = "x" * 201
    assert (
        visitor_client.post(url, {"version_id": version, "instruction": too_long}).status_code
        == 400
    )


def test_cancel_queued_edit_releases_quota(visitor_client):
    detail = make_ready_creation(visitor_client)
    response = visitor_client.post(
        f"/api/creations/{detail['id']}/edits/",
        {"version_id": detail["versions"][0]["id"], "instruction": "azul"},
    )
    task_id = response.data["edit_tasks"][0]["id"]
    cancel = visitor_client.post(f"/api/creations/{detail['id']}/edits/{task_id}/cancel/")
    assert cancel.status_code == 200
    drain_worker()
    assert len(visitor_client.get(f"/api/creations/{detail['id']}/").data["versions"]) == 1
    assert visitor_client.get("/api/quota/").data["edit"]["used"] == 0


def test_delete_hides_creation(visitor_client):
    creation_id = _create(visitor_client).data["id"]
    assert visitor_client.delete(f"/api/creations/{creation_id}/").status_code == 204
    assert visitor_client.get(f"/api/creations/{creation_id}/").status_code == 404
    assert visitor_client.get("/api/creations/").data["count"] == 0
