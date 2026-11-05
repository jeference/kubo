"""TEMPORARY: one uploaded image -> one 3D task per selected model.

A run lives on disk under MEDIA_ROOT (`comparisons/<id>/run.json`, `input.png`, `<key>.glb`),
so reloading the page neither loses nor pays again for what was generated. Each model
succeeds or fails on its own.
"""

from __future__ import annotations

import json
import struct
import threading
import time
import uuid
from pathlib import Path

import requests
import structlog
from django.conf import settings

from common.exceptions import NotFound, UpstreamUnavailable
from generation.services import normalize_png
from integrations.ports import get_generation_port

_DOWNLOAD_TIMEOUT_SECONDS = 120
_TIMEOUT_ERROR = "Tempo esgotado esperando o modelo."
_GLB_HEADER_BYTES = 12
_GLB_CHUNK_HEADER_BYTES = 8
# A poll can overlap the previous one (a reload, a second tab): they would download the same
# GLB and race on run.json.
_refresh_lock = threading.Lock()
log = structlog.get_logger(__name__)


def get_catalog() -> list[dict]:
    return [
        {
            "key": key,
            "label": spec["label"],
            "estimated_cost": spec["estimated_cost"],
            "settings": spec["settings"],
        }
        for key, spec in settings.MODEL_COMPARISON.items()
    ]


def _run_dir(run_id: uuid.UUID | str) -> Path:
    return Path(settings.MEDIA_ROOT) / "comparisons" / str(run_id)


def _media_url(run_id: str, filename: str) -> str:
    return f"{settings.MEDIA_URL}comparisons/{run_id}/{filename}"


def _write_run(run: dict) -> None:
    (_run_dir(run["id"]) / "run.json").write_text(json.dumps(run, indent=2), encoding="utf-8")


def _submit(key: str, png: bytes) -> dict:
    spec = settings.MODEL_COMPARISON[key]
    model = {
        "key": key,
        "label": spec["label"],
        "estimated_cost": spec["estimated_cost"],
        "settings": spec["settings"],
        "task_id": "",
        "submitted_at": time.time(),
        "status": "processing",
        "glb_url": "",
        "cost": None,
        "error": "",
        "seconds": None,
        "triangles": None,
        "file_bytes": None,
    }
    try:
        model["task_id"] = get_generation_port().submit_comparison_model(
            image=png,
            model=spec["model"],
            image_as_list=spec["image_as_list"],
            task_settings=spec["settings"],
        )
    except UpstreamUnavailable as exc:
        model.update(status="error", error=exc.detail)
    log.info("comparison_submitted", key=key, status=model["status"])
    return model


def create_run(*, raw: bytes, model_keys: list[str]) -> dict:
    png = normalize_png(raw)
    run_id = str(uuid.uuid4())
    _run_dir(run_id).mkdir(parents=True)
    (_run_dir(run_id) / "input.png").write_bytes(png)
    run = {"id": run_id, "image_url": _media_url(run_id, "input.png"), "models": []}
    for key in dict.fromkeys(model_keys):
        run["models"].append(_submit(key, png))
        # Saved per model: tasks already paid for must survive a failure in the next one.
        _write_run(run)
    return run


def _count_triangles(glb: bytes) -> int | None:
    """Read from the GLB's JSON chunk. Compressed meshes still declare their counts there."""
    try:
        length = struct.unpack_from("<I", glb, _GLB_HEADER_BYTES)[0]
        start = _GLB_HEADER_BYTES + _GLB_CHUNK_HEADER_BYTES
        gltf = json.loads(glb[start : start + length])
        accessors = gltf["accessors"]
        total = 0
        for mesh in gltf["meshes"]:
            for primitive in mesh["primitives"]:
                index = primitive.get("indices", primitive["attributes"]["POSITION"])
                total += accessors[index]["count"] // 3
        return total
    except (struct.error, ValueError, KeyError, IndexError, TypeError):
        return None


def _finish(run_id: str, model: dict, file_url: str, cost: float | None, elapsed: float) -> None:
    response = requests.get(file_url, timeout=_DOWNLOAD_TIMEOUT_SECONDS)
    response.raise_for_status()
    filename = f"{model['key']}.glb"
    (_run_dir(run_id) / filename).write_bytes(response.content)
    model.update(
        status="success",
        glb_url=_media_url(run_id, filename),
        cost=cost,
        seconds=round(elapsed),
        triangles=_count_triangles(response.content),
        file_bytes=len(response.content),
    )
    log.info("comparison_ready", key=model["key"], cost=cost, seconds=model["seconds"])


def _refresh(run_id: str, model: dict) -> bool:
    """Advance one processing model. Returns whether it changed."""
    elapsed = time.time() - model["submitted_at"]
    try:
        task = get_generation_port().get_model(task_id=model["task_id"])
        if task.status == "success":
            _finish(run_id, model, task.file_url, task.cost, elapsed)
            return True
        if task.status == "error":
            model.update(status="error", error=task.error, cost=task.cost)
            return True
    except (UpstreamUnavailable, requests.RequestException) as exc:
        # The task keeps running at the provider: the next poll tries again.
        log.warning("comparison_poll_failed", key=model["key"], error=str(exc))
    if elapsed > settings.MODEL_COMPARISON_TIMEOUT_SECONDS:
        model.update(status="error", error=_TIMEOUT_ERROR)
        return True
    return False


def get_run(*, run_id: uuid.UUID) -> dict:
    path = _run_dir(run_id) / "run.json"
    with _refresh_lock:
        if not path.exists():
            raise NotFound("Comparação não encontrada.")
        run = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for model in run["models"]:
            if model["status"] == "processing":
                changed = _refresh(run["id"], model) or changed
        if changed:
            _write_run(run)
    return run
