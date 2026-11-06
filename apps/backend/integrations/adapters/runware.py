"""Runware (https://runware.ai/docs): um endpoint REST que recebe uma lista de tarefas.

Sucesso: `{"data": [...]}`. Falha: `{"data": [], "errors": [{"code", "message"}]}`.
"""

from __future__ import annotations

import base64
import re
import uuid

import requests
import structlog
from django.conf import settings

from integrations.ports import (
    ContentRefused,
    GeneratedImage,
    ImageGenerationPort,
    ProviderPermanentError,
    ProviderTemporaryError,
)

_BASE_URL = "https://api.runware.ai/v1"
_TIMEOUT_SECONDS = 90
# A Runware não documenta um código único de recusa. Reconhecemos pela mensagem ou pelo código.
_REFUSAL = re.compile(r"safety|moderat|content.?policy|nsfw|inappropriate|sensitive", re.I)
log = structlog.get_logger(__name__)


def _to_data_uri(image: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(image).decode("ascii")


def _from_data_uri(data_uri: str) -> bytes:
    _, _, payload = data_uri.partition(",")
    return base64.b64decode(payload)


class _RunwareError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _is_refusal(error: _RunwareError) -> bool:
    return bool(_REFUSAL.search(error.code) or _REFUSAL.search(error.message))


def _post(task: dict, operation: str) -> list[dict]:
    headers = {
        "Authorization": f"Bearer {settings.RUNWARE_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(_BASE_URL, json=[task], headers=headers, timeout=_TIMEOUT_SECONDS)
        body = response.json()
    except (requests.RequestException, ValueError) as exc:
        log.warning("runware_request_failed", operation=operation, error=str(exc))
        raise ProviderTemporaryError("Runware indisponível.") from exc

    errors = body.get("errors") or ([body["error"]] if body.get("error") else [])
    if errors:
        error = errors[0] if isinstance(errors[0], dict) else {"message": str(errors[0])}
        code = str(error.get("code", "unknown"))
        message = str(error.get("message", "Erro desconhecido."))
        log.warning("runware_error", operation=operation, code=code, message=message)
        raise _RunwareError(code, message)
    if response.status_code == 429 or response.status_code >= 500:
        raise ProviderTemporaryError(f"Runware respondeu {response.status_code}.")
    if response.status_code >= 400:
        raise ProviderPermanentError(f"Runware respondeu {response.status_code}.")
    return body.get("data") or []


def _run(task: dict, operation: str) -> list[dict]:
    try:
        return _post(task, operation)
    except _RunwareError as exc:
        if _is_refusal(exc):
            raise ContentRefused(exc.message) from exc
        raise ProviderPermanentError(exc.message) from exc


class RunwareImageGenerationAdapter(ImageGenerationPort):
    provider = "runware"

    @property
    def model_name(self) -> str:
        return settings.RUNWARE_IMAGE_MODEL

    def _task(self, *, prompt: str, size: int) -> dict:
        return {
            "taskType": "imageInference",
            "taskUUID": str(uuid.uuid4()),
            "model": settings.RUNWARE_IMAGE_MODEL,
            "positivePrompt": prompt,
            "width": size,
            "height": size,
            "numberResults": 1,
            "outputType": "dataURI",
            "outputFormat": "PNG",
            "includeCost": True,
        }

    def _result(self, data: list[dict]) -> GeneratedImage:
        item = next((d for d in data if d.get("imageDataURI")), None)
        if item is None:
            raise ProviderPermanentError("Runware não devolveu a imagem.")
        return GeneratedImage(data=_from_data_uri(item["imageDataURI"]), cost_usd=item.get("cost"))

    def generate(self, *, prompt: str, size: int) -> GeneratedImage:
        return self._result(_run(self._task(prompt=prompt, size=size), "generate_image"))

    def edit(self, *, image: bytes, prompt: str, size: int) -> GeneratedImage:
        task = self._task(prompt=prompt, size=size)
        task["inputs"] = {"referenceImages": [_to_data_uri(image)]}
        return self._result(_run(task, "edit_image"))
