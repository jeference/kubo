"""Leitura mínima do JSON de um GLB: contagem de triângulos e presença de textura."""

from __future__ import annotations

import json
import struct

_MAGIC = 0x46546C67
_JSON_CHUNK = 0x4E4F534A


def _parse(glb: bytes) -> dict:
    if len(glb) < 20:
        return {}
    magic, _version, _length = struct.unpack_from("<III", glb, 0)
    chunk_length, chunk_type = struct.unpack_from("<II", glb, 12)
    if magic != _MAGIC or chunk_type != _JSON_CHUNK:
        return {}
    return json.loads(glb[20 : 20 + chunk_length])


def triangle_count(glb: bytes) -> int:
    document = _parse(glb)
    accessors = document.get("accessors", [])
    total = 0
    for mesh in document.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            if primitive.get("mode", 4) != 4:
                continue
            index = primitive.get("indices")
            if index is not None:
                total += accessors[index].get("count", 0) // 3
            else:
                position = primitive.get("attributes", {}).get("POSITION")
                if position is not None:
                    total += accessors[position].get("count", 0) // 3
    return total


def has_texture(glb: bytes) -> bool:
    """Evita entregar modelo cinza: exige ao menos um material com textura de cor."""
    document = _parse(glb)
    if not document.get("textures") or not document.get("images"):
        return False
    for material in document.get("materials", []):
        pbr = material.get("pbrMetallicRoughness", {})
        if "baseColorTexture" in pbr:
            return True
    return False
