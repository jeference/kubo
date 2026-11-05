"""Storage local, para desenvolvimento: arquivos em MEDIA_ROOT, servidos por `/api/media/`."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core import signing

from integrations.ports import MediaStoragePort

SIGNING_SALT = "kubo.media"


def _path(key: str) -> Path:
    root = Path(settings.MEDIA_ROOT).resolve()
    path = (root / key).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Chave de arquivo inválida.")
    return path


class LocalMediaAdapter(MediaStoragePort):
    def put(self, *, key: str, data: bytes, content_type: str) -> None:
        path = _path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def get(self, *, key: str) -> bytes | None:
        path = _path(key)
        return path.read_bytes() if path.is_file() else None

    def delete(self, *, key: str) -> None:
        _path(key).unlink(missing_ok=True)

    def signed_url(self, *, key: str, ttl_seconds: int, content_type: str = "") -> str:
        token = signing.dumps({"k": key, "t": ttl_seconds, "c": content_type}, salt=SIGNING_SALT)
        return f"/api/media/{token}/"
