import base64
import json

import pytest
import responses

from common.exceptions import UpstreamUnavailable
from integrations.adapters.runware import _BASE_URL, RunwareGenerationAdapter

PNG = b"\x89PNG fake"
DATA_URI = "data:image/png;base64," + base64.b64encode(PNG).decode()


@pytest.fixture
def adapter(settings):
    settings.RUNWARE_API_KEY = "test-key"
    return RunwareGenerationAdapter()


@responses.activate
def test_generate_images_decodes_data_uris(adapter):
    responses.post(
        _BASE_URL,
        json={
            "data": [
                {"taskType": "imageInference", "imageDataURI": DATA_URI, "cost": 0.0012},
                {"taskType": "imageInference", "imageDataURI": DATA_URI, "cost": 0.0012},
            ]
        },
    )

    images = adapter.generate_images(prompt="a fox", count=2, size=512)

    assert [image.data for image in images] == [PNG, PNG]
    assert images[0].cost == 0.0012
    sent = responses.calls[0].request
    assert sent.headers["Authorization"] == "Bearer test-key"
    assert b'"numberResults": 2' in sent.body


@responses.activate
def test_edit_image_sends_the_source_as_reference(adapter):
    responses.post(_BASE_URL, json={"data": [{"imageDataURI": DATA_URI, "cost": 0.0017}]})

    image = adapter.edit_image(image=b"source", prompt="make it red", size=512)

    assert image.data == PNG
    assert image.cost == 0.0017
    task = json.loads(responses.calls[0].request.body)[0]
    assert task["positivePrompt"] == "make it red"
    assert task["inputs"]["referenceImages"] == [
        "data:image/png;base64," + base64.b64encode(b"source").decode()
    ]


@responses.activate
def test_edit_image_without_output_is_upstream_unavailable(adapter):
    responses.post(_BASE_URL, json={"data": []})

    with pytest.raises(UpstreamUnavailable):
        adapter.edit_image(image=b"source", prompt="make it red", size=512)


@responses.activate
def test_api_error_becomes_upstream_unavailable(adapter):
    responses.post(
        _BASE_URL,
        status=400,
        json={"data": [], "errors": [{"code": "insufficientCredits", "message": "No credits"}]},
    )

    with pytest.raises(UpstreamUnavailable, match="No credits"):
        adapter.generate_images(prompt="a fox", count=1, size=512)


@responses.activate
def test_get_model_success(adapter):
    responses.post(
        _BASE_URL,
        json={
            "data": [
                {
                    "taskType": "3dInference",
                    "taskUUID": "t-1",
                    "cost": 0.03,
                    "outputs": {"files": [{"uuid": "f", "url": "https://x/model.glb"}]},
                }
            ]
        },
    )

    task = adapter.get_model(task_id="t-1")

    assert task.status == "success"
    assert task.file_url == "https://x/model.glb"
    assert task.cost == 0.03


@responses.activate
def test_get_model_processing_when_no_output_yet(adapter):
    responses.post(
        _BASE_URL,
        json={"data": [{"taskType": "3dInference", "taskUUID": "t-1", "status": "processing"}]},
    )

    assert adapter.get_model(task_id="t-1").status == "processing"


@responses.activate
def test_get_model_error(adapter):
    responses.post(
        _BASE_URL,
        status=400,
        json={"data": [], "errors": [{"code": "inferenceFailed", "message": "Bad image"}]},
    )

    task = adapter.get_model(task_id="t-1")

    assert task.status == "error"
    assert task.error == "Bad image"


@responses.activate
@pytest.mark.parametrize("balance", [20.0081, {"amount": 20.0081, "currency": "USD"}])
def test_get_credits(adapter, balance):
    responses.post(
        _BASE_URL,
        json={
            "data": [
                {
                    "taskType": "accountManagement",
                    "balance": balance,
                    "usage": {"total": {"credits": 0.0642, "requests": 31}},
                }
            ]
        },
    )

    credits = adapter.get_credits()

    assert credits.balance == 20.0081
    assert credits.total_spent == 0.0642
