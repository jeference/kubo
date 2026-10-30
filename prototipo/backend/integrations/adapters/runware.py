"""Runware adapter (https://runware.ai/docs).

Single REST endpoint: POST an array of tasks, get `{"data": [...]}` back, or
`{"data": [], "errors": [{"code", "message", ...}]}` on failure.
"""

from __future__ import annotations

import base64
import uuid

import requests
import structlog
from django.conf import settings

from common.exceptions import UpstreamUnavailable
from integrations.ports import AccountCredits, GeneratedImage, GenerationPort, ModelTask

_BASE_URL = "https://api.runware.ai/v1"
_TIMEOUT_SECONDS = 90
log = structlog.get_logger(__name__)


def _to_data_uri(image: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(image).decode("ascii")


def _from_data_uri(data_uri: str) -> bytes:
    _, _, payload = data_uri.partition(",")
    return base64.b64decode(payload)


class RunwareError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class RunwareGenerationAdapter(GenerationPort):
    def __init__(self) -> None:
        self._api_key = settings.RUNWARE_API_KEY

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    def _post(self, task: dict, operation: str) -> list[dict]:
        """Send one task and return its `data` items. Raises RunwareError on API errors."""
        try:
            response = requests.post(
                _BASE_URL, json=[task], headers=self._headers(), timeout=_TIMEOUT_SECONDS
            )
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            log.error("runware_request_failed", operation=operation, error=str(exc))
            raise UpstreamUnavailable("Runware indisponível.")

        errors = body.get("errors") or ([body["error"]] if body.get("error") else [])
        if errors:
            error = errors[0] if isinstance(errors[0], dict) else {"message": str(errors[0])}
            code = error.get("code", "unknown")
            message = error.get("message", "Erro desconhecido.")
            log.error("runware_error", operation=operation, code=code, message=message)
            raise RunwareError(code, message)
        if response.status_code >= 400:
            log.error("runware_http_error", operation=operation, status=response.status_code)
            raise UpstreamUnavailable("Runware retornou erro.")
        return body.get("data") or []

    def _run(self, task: dict, operation: str) -> list[dict]:
        try:
            return self._post(task, operation)
        except RunwareError as exc:
            raise UpstreamUnavailable(f"Runware: {exc.message}")

    def generate_images(self, *, prompt: str, count: int, size: int) -> list[GeneratedImage]:
        data = self._run(
            {
                "taskType": "imageInference",
                "taskUUID": str(uuid.uuid4()),
                "model": settings.RUNWARE_IMAGE_MODEL,
                "positivePrompt": prompt,
                "width": size,
                "height": size,
                "numberResults": count,
                "outputType": "dataURI",
                "outputFormat": "PNG",
                "includeCost": True,
            },
            "generate_images",
        )
        return [
            GeneratedImage(data=_from_data_uri(item["imageDataURI"]), cost=item.get("cost"))
            for item in data
            if item.get("imageDataURI")
        ]

    def submit_model(self, *, image: bytes) -> str:
        task_id = str(uuid.uuid4())
        self._run(
            {
                "taskType": "3dInference",
                "taskUUID": task_id,
                "model": settings.RUNWARE_3D_MODEL,
                "deliveryMethod": "async",
                "outputType": "URL",
                "outputFormat": "GLB",
                "includeCost": True,
                "inputs": {"image": _to_data_uri(image)},
                "settings": settings.TRELLIS_SETTINGS,
            },
            "submit_model",
        )
        return task_id

    def get_model(self, *, task_id: str) -> ModelTask:
        # getResponse format not yet confirmed against a real 3D task — parsed defensively.
        try:
            data = self._post({"taskType": "getResponse", "taskUUID": task_id}, "get_model")
        except RunwareError as exc:
            return ModelTask(status="error", error=exc.message)

        item = next((d for d in data if d.get("taskUUID") == task_id), None)
        if item is None:
            return ModelTask(status="processing")

        files = (item.get("outputs") or {}).get("files") or []
        if files and files[0].get("url"):
            return ModelTask(status="success", file_url=files[0]["url"], cost=item.get("cost"))
        if item.get("status") == "error":
            return ModelTask(status="error", error=item.get("message", "Falha ao gerar o modelo."))
        return ModelTask(status="processing")

    def get_credits(self) -> AccountCredits:
        data = self._run(
            {
                "taskType": "accountManagement",
                "taskUUID": str(uuid.uuid4()),
                "operation": "getDetails",
            },
            "get_credits",
        )
        if not data:
            raise UpstreamUnavailable("Runware não retornou os dados da conta.")
        balance = data[0].get("balance")
        # The live API returns a plain number; the docs describe {"amount", "currency"}.
        if isinstance(balance, dict):
            balance = balance.get("amount")
        total = ((data[0].get("usage") or {}).get("total") or {}).get("credits")
        return AccountCredits(balance=float(balance or 0), total_spent=float(total or 0))
