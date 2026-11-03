"""Generation flow: prompt and/or uploaded photo -> image -> edits -> 3D model.

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
from PIL import Image, ImageOps, ImageStat, UnidentifiedImageError

from common.exceptions import InvalidImage, NotFound, UpstreamUnavailable
from integrations.ports import AccountCredits, get_generation_port

_DOWNLOAD_TIMEOUT_SECONDS = 60
# A plain near-white background: every border strip has a median at least this bright and
# varies at most this much (flagged exactly the off-white images in the edit test).
_BACKGROUND_MIN_MEDIAN = 245
_BACKGROUND_MAX_STDDEV = 5
_BACKGROUND_STRIP_RATIO = 0.02
_BACKGROUND_LOST_WARNING = (
    "O fundo saiu do branco, o que pode piorar o modelo 3D. "
    "Escolha outra versão ou peça para voltar ao fundo branco."
)
log = structlog.get_logger(__name__)


@dataclass(frozen=True)
class StoredImage:
    id: str
    url: str
    cost: float | None = None
    warning: str = ""


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


def _store_image(data: bytes, cost: float | None = None, warning: str = "") -> StoredImage:
    image_id = str(uuid.uuid4())
    (_media_dir("images") / f"{image_id}.png").write_bytes(data)
    return StoredImage(
        id=image_id, url=_media_url("images", f"{image_id}.png"), cost=cost, warning=warning
    )


def _read_image(image_id: uuid.UUID) -> bytes:
    path = _media_dir("images") / f"{image_id}.png"
    if not path.exists():
        raise NotFound("Imagem não encontrada.")
    return path.read_bytes()


def _background_is_plain(png: bytes) -> bool:
    image = Image.open(io.BytesIO(png)).convert("RGB")
    width, height = image.size
    strip = max(1, int(min(width, height) * _BACKGROUND_STRIP_RATIO))
    strips = [
        (0, 0, width, strip),
        (0, height - strip, width, height),
        (0, 0, strip, height),
        (width - strip, 0, width, height),
    ]
    for box in strips:
        stat = ImageStat.Stat(image.crop(box))
        if min(stat.median) < _BACKGROUND_MIN_MEDIAN or max(stat.stddev) > _BACKGROUND_MAX_STDDEV:
            return False
    return True


def normalize_png(raw: bytes) -> bytes:
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


def build_image_prompt(*, prompt: str, style: str = settings.DEFAULT_STYLE) -> str:
    subject = prompt.strip().rstrip(".")
    return settings.GENERATION["STYLES"][style]["PROMPT_TEMPLATE"].format(
        prompt=subject, prompt_lower=subject[:1].lower() + subject[1:]
    )


def build_edit_prompt(*, instruction: str) -> str:
    return settings.GENERATION["EDIT_PROMPT_TEMPLATE"].format(
        instruction=instruction.strip().rstrip(".")
    )


def build_standardize_prompt(*, request: str, style: str = settings.DEFAULT_STYLE) -> str:
    templates = settings.GENERATION["STYLES"][style]
    request = request.strip().rstrip(".")
    if not request:
        return templates["STANDARDIZE_PROMPT_TEMPLATE"]
    return templates["STANDARDIZE_REQUEST_PROMPT_TEMPLATE"].format(request=request)


def generate_images(*, prompt: str, style: str = settings.DEFAULT_STYLE) -> list[StoredImage]:
    images = get_generation_port().generate_images(
        prompt=build_image_prompt(prompt=prompt, style=style),
        count=settings.GENERATION["IMAGES_PER_PROMPT"],
        size=settings.GENERATION["IMAGE_SIZE"],
    )
    return [_store_image(image.data, image.cost) for image in images]


def edit_image(*, image_id: uuid.UUID, instruction: str) -> StoredImage:
    source = _read_image(image_id)
    edited = get_generation_port().edit_image(
        image=source,
        prompt=build_edit_prompt(instruction=instruction),
        size=settings.GENERATION["IMAGE_SIZE"],
    )
    # Only warn when the edit is what lost the background, not if it was never plain.
    background_lost = _background_is_plain(source) and not _background_is_plain(edited.data)
    return _store_image(
        edited.data, edited.cost, warning=_BACKGROUND_LOST_WARNING if background_lost else ""
    )


def standardize_upload(
    *, raw: bytes, prompt: str = "", style: str = settings.DEFAULT_STYLE
) -> StoredImage:
    image = get_generation_port().edit_image(
        image=normalize_png(raw),
        prompt=build_standardize_prompt(request=prompt, style=style),
        size=settings.GENERATION["IMAGE_SIZE"],
    )
    return _store_image(image.data, image.cost)


def create_model(*, image_id: uuid.UUID) -> ModelStatus:
    png = _read_image(image_id)
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


def get_credits() -> AccountCredits:
    return get_generation_port().get_credits()
