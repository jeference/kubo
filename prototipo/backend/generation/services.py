"""Generation flow: prompt (or uploaded photo) -> images -> 3D model.

State lives on disk under MEDIA_ROOT (`images/<id>.png`, `models/<id>.png|.glb`), so the
prototype needs no database: a model is "done" once its GLB has been downloaded.
"""

from __future__ import annotations

import io
import uuid
from dataclasses import dataclass
from pathlib import Path

import requests
import structlog
from django.conf import settings
from PIL import Image, ImageOps, UnidentifiedImageError

from common.exceptions import InvalidImage, NotFound, UpstreamUnavailable
from integrations.ports import get_generation_port

_DOWNLOAD_TIMEOUT_SECONDS = 60
log = structlog.get_logger(__name__)


@dataclass(frozen=True)
class StoredImage:
    id: str
    url: str
    cost: float | None = None


@dataclass(frozen=True)
class ModelStatus:
    id: str
    status: str  # processing | success | error
    glb_url: str = ""
    cost: float | None = None
    error: str = ""


def _media_dir(name: str) -> Path:
    path = Path(settings.MEDIA_ROOT) / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def _media_url(folder: str, filename: str) -> str:
    return f"{settings.MEDIA_URL}{folder}/{filename}"


def _store_image(data: bytes, cost: float | None = None) -> StoredImage:
    image_id = str(uuid.uuid4())
    (_media_dir("images") / f"{image_id}.png").write_bytes(data)
    return StoredImage(id=image_id, url=_media_url("images", f"{image_id}.png"), cost=cost)


def _normalize_png(raw: bytes) -> bytes:
    """Any uploaded image -> upright PNG no larger than IMAGE_SIZE, alpha preserved."""
    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError):
        raise InvalidImage()
    image = ImageOps.exif_transpose(image)
    has_alpha = image.mode in ("RGBA", "LA") or "transparency" in image.info
    image = image.convert("RGBA" if has_alpha else "RGB")
    max_side = settings.GENERATION["IMAGE_SIZE"]
    image.thumbnail((max_side, max_side))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def build_image_prompt(*, prompt: str) -> str:
    return f"{prompt.strip()}, {settings.GENERATION['PROMPT_STYLE_SUFFIX']}"


def generate_images(*, prompt: str) -> list[StoredImage]:
    images = get_generation_port().generate_images(
        prompt=build_image_prompt(prompt=prompt),
        count=settings.GENERATION["IMAGES_PER_PROMPT"],
        size=settings.GENERATION["IMAGE_SIZE"],
    )
    return [_store_image(image.data, image.cost) for image in images]


def save_upload(*, raw: bytes) -> StoredImage:
    return _store_image(_normalize_png(raw))


def create_model(*, image_id: uuid.UUID) -> ModelStatus:
    path = _media_dir("images") / f"{image_id}.png"
    if not path.exists():
        raise NotFound("Imagem não encontrada.")
    png = path.read_bytes()
    task_id = get_generation_port().submit_model(image=png)
    # Keep the exact input next to the output: it's what Tripo will get later.
    (_media_dir("models") / f"{task_id}.png").write_bytes(png)
    log.info("model_submitted", task_id=task_id)
    return ModelStatus(id=task_id, status="processing")


def get_model(*, task_id: uuid.UUID) -> ModelStatus:
    models = _media_dir("models")
    glb_path = models / f"{task_id}.glb"
    glb_url = _media_url("models", f"{task_id}.glb")
    if glb_path.exists():
        return ModelStatus(id=str(task_id), status="success", glb_url=glb_url)
    if not (models / f"{task_id}.png").exists():
        raise NotFound("Modelo não encontrado.")

    task = get_generation_port().get_model(task_id=str(task_id))
    if task.status != "success":
        return ModelStatus(id=str(task_id), status=task.status, error=task.error)

    try:
        response = requests.get(task.file_url, timeout=_DOWNLOAD_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        log.error("model_download_failed", task_id=str(task_id), error=str(exc))
        raise UpstreamUnavailable("Não foi possível baixar o modelo 3D.")
    glb_path.write_bytes(response.content)
    log.info("model_ready", task_id=str(task_id), cost=task.cost)
    return ModelStatus(id=str(task_id), status="success", glb_url=glb_url, cost=task.cost)
