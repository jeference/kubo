import io
import uuid
from pathlib import Path

import pytest
import responses
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from generation import services
from integrations.adapters import runware_stub
from integrations.ports import GeneratedImage


@pytest.fixture
def client():
    return APIClient()


def _png_upload(name="photo.png", color="red"):
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), color).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def _media_path(url: str) -> Path:
    return Path(settings.MEDIA_ROOT) / url.removeprefix(settings.MEDIA_URL)


def test_generate_images_stores_variations(client):
    response = client.post("/api/generation/images/", {"prompt": "uma raposa"})

    assert response.status_code == 201
    assert len(response.data) == settings.GENERATION["IMAGES_PER_PROMPT"]
    assert all(_media_path(image["url"]).exists() for image in response.data)


def test_generate_images_requires_prompt(client):
    response = client.post("/api/generation/images/", {"prompt": ""})

    assert response.status_code == 400


def test_upload_rejects_non_images(client):
    bogus = SimpleUploadedFile("notes.txt", b"hello", content_type="text/plain")

    response = client.post("/api/generation/images/upload/", {"image": bogus}, format="multipart")

    assert response.status_code == 422
    assert response.data["code"] == "invalid_image"


def test_upload_stores_png(client):
    response = client.post(
        "/api/generation/images/upload/", {"image": _png_upload()}, format="multipart"
    )

    assert response.status_code == 201
    assert Image.open(_media_path(response.data["url"])).format == "PNG"


def test_upload_standardizes_the_photo(client, monkeypatch):
    calls = []

    def fake_edit(self, *, image, prompt, size):
        calls.append((image, prompt))
        return GeneratedImage(data=_png_bytes("white"), cost=0.014)

    monkeypatch.setattr(runware_stub.StubGenerationAdapter, "edit_image", fake_edit)

    response = client.post(
        "/api/generation/images/upload/", {"image": _png_upload()}, format="multipart"
    )

    assert response.data["cost"] == 0.014
    stored = Image.open(_media_path(response.data["url"])).convert("RGB")
    assert stored.getpixel((0, 0)) == (255, 255, 255)  # the result, not the red photo
    image, prompt = calls[0]
    assert Image.open(io.BytesIO(image)).convert("RGB").getpixel((0, 0)) == (255, 0, 0)
    assert prompt == settings.GENERATION["STYLES"]["free"]["STANDARDIZE_PROMPT_TEMPLATE"]


def test_generate_images_uses_the_chosen_style(client, monkeypatch):
    calls = []

    def fake_generate(self, *, prompt, count, size):
        calls.append(prompt)
        return [GeneratedImage(data=_png_bytes("white"), cost=0)]

    monkeypatch.setattr(runware_stub.StubGenerationAdapter, "generate_images", fake_generate)

    response = client.post("/api/generation/images/", {"prompt": "uma raposa", "style": "chibi"})

    assert response.status_code == 201
    assert "uma raposa, as a Japanese chibi anime collectible figure" in calls[0]


def test_upload_uses_the_chosen_style(client, monkeypatch):
    calls = []

    def fake_edit(self, *, image, prompt, size):
        calls.append(prompt)
        return GeneratedImage(data=_png_bytes("white"), cost=0)

    monkeypatch.setattr(runware_stub.StubGenerationAdapter, "edit_image", fake_edit)

    client.post(
        "/api/generation/images/upload/",
        {"image": _png_upload(), "style": "mini-pop"},
        format="multipart",
    )
    client.post(
        "/api/generation/images/upload/",
        {"image": _png_upload(), "style": "pixar", "prompt": "de chapéu"},
        format="multipart",
    )

    assert "into a collectible vinyl bobble-head toy figure:" in calls[0]
    assert "from a modern animated family movie, with this one change: de chapéu." in calls[1]


def test_style_defaults_to_free(client, monkeypatch):
    calls = []

    def fake_generate(self, *, prompt, count, size):
        calls.append(prompt)
        return [GeneratedImage(data=_png_bytes("white"), cost=0)]

    monkeypatch.setattr(runware_stub.StubGenerationAdapter, "generate_images", fake_generate)

    client.post("/api/generation/images/", {"prompt": "uma raposa"})

    assert "uma raposa, as a detailed 3D figurine" in calls[0]


@pytest.mark.parametrize("url", ["/api/generation/images/", "/api/generation/images/upload/"])
def test_unknown_style_is_rejected(client, url):
    response = client.post(
        url,
        {"prompt": "uma raposa", "image": _png_upload(), "style": "cubismo"},
        format="multipart",
    )

    assert response.status_code == 400


def test_upload_passes_the_optional_prompt(client, monkeypatch):
    calls = []

    def fake_edit(self, *, image, prompt, size):
        calls.append(prompt)
        return GeneratedImage(data=_png_bytes("white"), cost=0)

    monkeypatch.setattr(runware_stub.StubGenerationAdapter, "edit_image", fake_edit)

    client.post(
        "/api/generation/images/upload/",
        {"image": _png_upload(), "prompt": " de chapéu {azul}. "},
        format="multipart",
    )

    assert "with this one change: de chapéu {azul}. Apart" in calls[0]


def _png_bytes(color):
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), color).save(buffer, format="PNG")
    return buffer.getvalue()


def _upload(client, color="white"):
    return client.post(
        "/api/generation/images/upload/", {"image": _png_upload(color=color)}, format="multipart"
    ).data


def test_edit_image_stores_a_new_version(client):
    source = _upload(client)

    response = client.post(
        f"/api/generation/images/{source['id']}/edit/", {"instruction": "chapéu vermelho"}
    )

    assert response.status_code == 201
    assert response.data["id"] != source["id"]
    assert response.data["warning"] == ""
    assert _media_path(response.data["url"]).exists()


def test_edit_image_sends_source_and_wrapped_instruction(client, monkeypatch):
    source = _upload(client)
    calls = []

    def fake_edit(self, *, image, prompt, size):
        calls.append((image, prompt))
        return GeneratedImage(data=_png_bytes("white"), cost=0.002)

    monkeypatch.setattr(runware_stub.StubGenerationAdapter, "edit_image", fake_edit)

    response = client.post(
        f"/api/generation/images/{source['id']}/edit/", {"instruction": " Tira o chapéu. "}
    )

    assert response.data["cost"] == 0.002
    image, prompt = calls[0]
    assert image == _media_path(source["url"]).read_bytes()
    assert "Tira o chapéu. Keep everything else" in prompt


def test_edit_image_unknown_image(client):
    response = client.post(f"/api/generation/images/{uuid.uuid4()}/edit/", {"instruction": "x"})

    assert response.status_code == 404


@pytest.mark.parametrize("instruction", ["", "x" * 201])
def test_edit_image_validates_instruction(client, instruction):
    source = _upload(client)

    response = client.post(
        f"/api/generation/images/{source['id']}/edit/", {"instruction": instruction}
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    ("source_color", "edited_color", "warns"),
    [("white", "red", True), ("white", "white", False), ("red", "blue", False)],
)
def test_edit_image_warns_only_when_the_edit_loses_the_background(
    client, monkeypatch, source_color, edited_color, warns
):
    source_id = services._store_image(_png_bytes(source_color)).id
    monkeypatch.setattr(
        runware_stub.StubGenerationAdapter,
        "edit_image",
        lambda self, **_: GeneratedImage(data=_png_bytes(edited_color), cost=0),
    )

    response = client.post(f"/api/generation/images/{source_id}/edit/", {"instruction": "x"})

    assert bool(response.data["warning"]) is warns


def test_create_model_unknown_image(client):
    response = client.post("/api/generation/models/", {"image_id": str(uuid.uuid4())})

    assert response.status_code == 404


@responses.activate
def test_model_flow_processing_then_success(client, monkeypatch):
    responses.add_passthru("http://testserver")
    responses.get(runware_stub._SAMPLE_GLB_URL, body=b"glTF-binary")
    uploaded = client.post(
        "/api/generation/images/upload/", {"image": _png_upload()}, format="multipart"
    )

    created = client.post("/api/generation/models/", {"image_id": uploaded.data["id"]})
    assert created.status_code == 202
    model_id = created.data["id"]

    assert client.get(f"/api/generation/models/{model_id}/").data["status"] == "processing"

    monkeypatch.setattr(runware_stub, "_MODEL_SECONDS", 0)
    done = client.get(f"/api/generation/models/{model_id}/")

    assert done.data["status"] == "success"
    assert _media_path(done.data["glb_url"]).read_bytes() == b"glTF-binary"


def test_unknown_model(client):
    response = client.get(f"/api/generation/models/{uuid.uuid4()}/")

    assert response.status_code == 404


def test_credits(client):
    response = client.get("/api/generation/credits/")

    assert response.status_code == 200
    assert response.data == {"balance": 20.0, "total_spent": 0.0}


def test_build_image_prompt_wraps_description():
    prompt = services.build_image_prompt(prompt="  Uma coruja {de} óculos. ")

    assert "Uma coruja {de} óculos, as a detailed 3D figurine" in prompt
    assert "isolated on a plain white background\n\nColor plan" in prompt


@pytest.mark.parametrize(
    "prompt",
    [
        services.build_image_prompt(prompt="uma coruja"),
        services.build_edit_prompt(instruction="tira o chapéu"),
        services.build_standardize_prompt(request=""),
        services.build_standardize_prompt(request="de chapéu"),
    ],
    ids=["image", "edit", "upload", "upload_with_request"],
)
def test_prompts_limit_colors_to_the_filaments(prompt):
    assert f"at most {settings.MAX_PRINT_COLORS} of them" in prompt
    assert all(hex_code in prompt for hex_code in settings.FILAMENT_COLORS.values())
    assert "true-to-life" not in prompt


@pytest.mark.parametrize("style", list(settings.GENERATION["STYLES"]))
def test_every_style_builds_its_three_prompts(style):
    prompts = [
        services.build_image_prompt(prompt="uma {coruja}", style=style),
        services.build_standardize_prompt(request="", style=style),
        services.build_standardize_prompt(request="de {chapéu}", style=style),
    ]

    assert "uma {coruja}" in prompts[0]
    assert "de {chapéu}" in prompts[2]
    for prompt in prompts:
        assert f"at most {settings.MAX_PRINT_COLORS} of them" in prompt
        assert "plain white background" in prompt
        assert f"exactly {settings.MAX_PRINT_COLORS} colors" in prompt
        assert prompt.endswith("not in the request or the reference.")
        assert "colors and distinctive" not in prompt
        assert "skin tone" not in prompt
