import io
import json
import struct
import uuid
from pathlib import Path

import pytest
import requests
import responses
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from common.exceptions import UpstreamUnavailable
from comparison import services
from integrations.adapters import runware_stub
from integrations.adapters.runware_stub import StubGenerationAdapter
from integrations.ports import ModelTask


@pytest.fixture
def client():
    return APIClient()


def _png_upload():
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), "red").save(buffer, format="PNG")
    return SimpleUploadedFile("photo.png", buffer.getvalue(), content_type="image/png")


def _create(client, models):
    return client.post(
        "/api/comparison/runs/", {"image": _png_upload(), "models": models}, format="multipart"
    )


def _glb(triangles):
    gltf = {
        "accessors": [{"count": triangles * 3}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 0}]}],
    }
    chunk = json.dumps(gltf).encode()
    return b"glTF" + struct.pack("<II", 2, 0) + struct.pack("<II", len(chunk), 0) + chunk


def _finish_tasks(monkeypatch, cost=0.5):
    monkeypatch.setattr(
        StubGenerationAdapter,
        "get_model",
        lambda self, *, task_id: ModelTask(
            status="success", file_url=runware_stub._SAMPLE_GLB_URL, cost=cost
        ),
    )


def test_catalog_lists_configured_models(client):
    response = client.get("/api/comparison/models/")

    assert response.status_code == 200
    assert [model["key"] for model in response.data] == list(settings.MODEL_COMPARISON)
    assert all(model["estimated_cost"] > 0 for model in response.data)


def test_create_run_submits_only_selected_models(client, monkeypatch):
    calls = []
    original = StubGenerationAdapter.submit_comparison_model

    def spy(self, **kwargs):
        calls.append(kwargs)
        return original(self, **kwargs)

    monkeypatch.setattr(StubGenerationAdapter, "submit_comparison_model", spy)

    response = _create(client, ["trellis", "meshy"])

    assert response.status_code == 202
    assert [model["key"] for model in response.data["models"]] == ["trellis", "meshy"]
    assert all(model["status"] == "processing" for model in response.data["models"])
    assert [(call["model"], call["image_as_list"]) for call in calls] == [
        ("microsoft:trellis-2@4b", False),
        ("meshy:meshy@6", True),
    ]
    assert calls[1]["task_settings"] == settings.MODEL_COMPARISON["meshy"]["settings"]


def test_create_run_rejects_unknown_model(client):
    assert _create(client, ["nope"]).status_code == 400


def test_create_run_requires_a_model(client):
    response = client.post("/api/comparison/runs/", {"image": _png_upload()}, format="multipart")

    assert response.status_code == 400


def test_invalid_image_submits_nothing(client, monkeypatch):
    def fail(self, **kwargs):
        raise AssertionError("must not spend credits on an invalid image")

    monkeypatch.setattr(StubGenerationAdapter, "submit_comparison_model", fail)
    bogus = SimpleUploadedFile("notes.txt", b"hello", content_type="text/plain")

    response = client.post(
        "/api/comparison/runs/", {"image": bogus, "models": ["trellis"]}, format="multipart"
    )

    assert response.status_code == 422


def test_submit_failure_stays_on_its_model(client, monkeypatch):
    original = StubGenerationAdapter.submit_comparison_model

    def flaky(self, *, model, **kwargs):
        if model == "tripo:v3.1@0":
            raise UpstreamUnavailable("Runware: sem crédito")
        return original(self, model=model, **kwargs)

    monkeypatch.setattr(StubGenerationAdapter, "submit_comparison_model", flaky)

    response = _create(client, ["tripo", "trellis"])

    tripo, trellis = response.data["models"]
    assert tripo["status"] == "error"
    assert tripo["error"] == "Runware: sem crédito"
    assert trellis["status"] == "processing"


def test_poll_error_task_stays_on_its_model(client, monkeypatch):
    created = _create(client, ["trellis"])
    monkeypatch.setattr(
        StubGenerationAdapter,
        "get_model",
        lambda self, *, task_id: ModelTask(status="error", error="Falhou"),
    )

    model = client.get(f"/api/comparison/runs/{created.data['id']}/").data["models"][0]

    assert model["status"] == "error"
    assert model["error"] == "Falhou"


@responses.activate
def test_finished_model_keeps_cost_and_stats_between_polls(client, monkeypatch):
    responses.add_passthru("http://testserver")
    responses.get(runware_stub._SAMPLE_GLB_URL, body=_glb(triangles=7))
    created = _create(client, ["trellis"])
    url = f"/api/comparison/runs/{created.data['id']}/"
    _finish_tasks(monkeypatch, cost=0.0409)

    first = client.get(url).data["models"][0]
    assert first["status"] == "success"
    assert first["cost"] == 0.0409
    assert first["triangles"] == 7
    assert first["file_bytes"] == len(_glb(triangles=7))
    path = Path(settings.MEDIA_ROOT) / first["glb_url"].removeprefix(settings.MEDIA_URL)
    assert path.read_bytes() == _glb(triangles=7)

    def fail(self, *, task_id):
        raise AssertionError("a finished model must not be polled again")

    monkeypatch.setattr(StubGenerationAdapter, "get_model", fail)
    assert client.get(url).data["models"][0]["cost"] == 0.0409


@responses.activate
def test_missing_cost_stays_null_and_bad_glb_has_no_stats(client, monkeypatch):
    responses.add_passthru("http://testserver")
    responses.get(runware_stub._SAMPLE_GLB_URL, body=b"not a glb")
    created = _create(client, ["trellis"])
    _finish_tasks(monkeypatch, cost=None)

    model = client.get(f"/api/comparison/runs/{created.data['id']}/").data["models"][0]

    assert model["status"] == "success"
    assert model["cost"] is None
    assert model["triangles"] is None


def test_network_failure_keeps_processing(client, monkeypatch):
    created = _create(client, ["trellis"])

    def down(self, *, task_id):
        raise UpstreamUnavailable("Runware indisponível.")

    monkeypatch.setattr(StubGenerationAdapter, "get_model", down)

    model = client.get(f"/api/comparison/runs/{created.data['id']}/").data["models"][0]

    assert model["status"] == "processing"


@responses.activate
def test_download_failure_retries_on_next_poll(client, monkeypatch):
    responses.add_passthru("http://testserver")
    responses.get(runware_stub._SAMPLE_GLB_URL, body=requests.ConnectionError("down"))
    responses.get(runware_stub._SAMPLE_GLB_URL, body=_glb(triangles=1))
    created = _create(client, ["trellis"])
    url = f"/api/comparison/runs/{created.data['id']}/"
    _finish_tasks(monkeypatch)

    assert client.get(url).data["models"][0]["status"] == "processing"
    assert client.get(url).data["models"][0]["status"] == "success"


def test_timeout_turns_into_error(client, settings):
    created = _create(client, ["trellis"])
    settings.MODEL_COMPARISON_TIMEOUT_SECONDS = -1

    model = client.get(f"/api/comparison/runs/{created.data['id']}/").data["models"][0]

    assert model["status"] == "error"
    assert model["error"] == services._TIMEOUT_ERROR


def test_unknown_run(client):
    assert client.get(f"/api/comparison/runs/{uuid.uuid4()}/").status_code == 404
