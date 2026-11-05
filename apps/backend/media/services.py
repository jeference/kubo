from __future__ import annotations

import hashlib
import io
import uuid

from django.conf import settings
from django.utils import timezone
from PIL import Image, ImageOps, UnidentifiedImageError

from common.exceptions import GuardFailed
from integrations.ports import get_media_storage_port
from media.models import Asset

_EXTENSIONS = {"image/png": "png", "model/gltf-binary": "glb"}
_ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}


def store(*, data: bytes, kind: str, mime: str) -> Asset:
    key = f"{kind}/{uuid.uuid4().hex}.{_EXTENSIONS.get(mime, 'bin')}"
    get_media_storage_port().put(key=key, data=data, content_type=mime)
    return Asset.objects.create(
        key=key,
        kind=kind,
        mime=mime,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def read(asset: Asset) -> bytes:
    data = get_media_storage_port().get(key=asset.key)
    if data is None:
        raise GuardFailed("Arquivo indisponível.", code="asset_missing")
    return data


def signed_url(asset: Asset | None) -> str:
    if asset is None or asset.purged_at is not None:
        return ""
    return get_media_storage_port().signed_url(
        key=asset.key,
        ttl_seconds=settings.BUSINESS["SIGNED_URL_TTL_SECONDS"],
        content_type=asset.mime,
    )


def purge(asset: Asset) -> None:
    """Apaga o arquivo e mantém o registro."""
    if asset.purged_at is not None:
        return
    get_media_storage_port().delete(key=asset.key)
    asset.purged_at = timezone.now()
    asset.save(update_fields=["purged_at", "updated_at"])


def normalize_photo(raw: bytes) -> bytes:
    """Foto enviada -> PNG em pé, com no máximo IMAGE_SIZE. Valida o tipo real do arquivo."""
    if len(raw) > settings.BUSINESS["PHOTO_MAX_BYTES"]:
        raise GuardFailed("A foto deve ter no máximo 10 MB.", code="photo_too_large")
    try:
        image = Image.open(io.BytesIO(raw))
        if image.format not in _ALLOWED_FORMATS:
            raise GuardFailed("Envie uma foto em PNG, JPG ou WEBP.", code="photo_invalid")
        image.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise GuardFailed("Não conseguimos ler essa foto.", code="photo_invalid") from exc
    image = ImageOps.exif_transpose(image)
    has_alpha = image.mode in ("RGBA", "LA") or "transparency" in image.info
    image = image.convert("RGBA" if has_alpha else "RGB")
    max_side = settings.BUSINESS["IMAGE_SIZE"]
    image.thumbnail((max_side, max_side))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
