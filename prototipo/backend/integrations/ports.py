"""Generation port (image + 3D) and its resolver.

Every external AI call lives behind `GenerationPort`. The adapter is picked by the
`GENERATION_ADAPTER` dotted path, so the UI can be exercised offline with the stub.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cache

from django.conf import settings
from django.utils.module_loading import import_string


@dataclass(frozen=True)
class GeneratedImage:
    data: bytes  # PNG bytes
    cost: float | None = None


@dataclass(frozen=True)
class ModelTask:
    status: str  # processing | success | error
    file_url: str = ""
    cost: float | None = None
    error: str = ""


class GenerationPort(ABC):
    @abstractmethod
    def generate_images(self, *, prompt: str, count: int, size: int) -> list[GeneratedImage]:
        """Text -> `count` square PNG images."""

    @abstractmethod
    def submit_model(self, *, image: bytes) -> str:
        """Start an async image -> 3D (GLB) task. Returns the task id."""

    @abstractmethod
    def get_model(self, *, task_id: str) -> ModelTask:
        """Current state of a 3D task started by `submit_model`."""


@cache
def _resolve(setting_name: str):
    return import_string(getattr(settings, setting_name))()


def reset_ports() -> None:
    _resolve.cache_clear()


def get_generation_port() -> GenerationPort:
    return _resolve("GENERATION_ADAPTER")
