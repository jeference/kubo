from __future__ import annotations

import io

import pytest
from PIL import Image

from common.exceptions import GuardFailed
from media import services
from media.models import Asset


def test_signed_url_serves_file_and_rejects_tampering(anon):
    asset = services.store(data=b"conteudo", kind=Asset.Kind.IMAGE, mime="image/png")
    url = services.signed_url(asset)
    response = anon.get(url)
    assert response.status_code == 200
    assert response.content == b"conteudo"
    assert anon.get(url[:-3] + "xx/").status_code == 404


def test_purged_asset_has_no_url():
    asset = services.store(data=b"x", kind=Asset.Kind.PHOTO, mime="image/png")
    services.purge(asset)
    assert services.signed_url(asset) == ""


def test_normalize_photo_limits_size_and_validates_type():
    buffer = io.BytesIO()
    Image.new("RGB", (2000, 1000)).save(buffer, format="JPEG")
    normalized = Image.open(io.BytesIO(services.normalize_photo(buffer.getvalue())))
    assert normalized.format == "PNG"
    assert max(normalized.size) == 1024
    with pytest.raises(GuardFailed):
        services.normalize_photo(b"isto nao e imagem")
    gif = io.BytesIO()
    Image.new("RGB", (10, 10)).save(gif, format="GIF")
    with pytest.raises(GuardFailed):
        services.normalize_photo(gif.getvalue())
