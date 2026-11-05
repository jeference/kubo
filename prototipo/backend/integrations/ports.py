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


@dataclass(frozen=True)
class AccountCredits:
    """Provider account, in USD."""

    balance: float
    total_spent: float


class GenerationPort(ABC):
    @abstractmethod
    def generate_images(self, *, prompt: str, count: int, size: int) -> list[GeneratedImage]:
        """Text -> `count` square PNG images."""

    @abstractmethod
    def edit_image(self, *, image: bytes, prompt: str, size: int) -> GeneratedImage:
        """Image + instruction -> the edited square PNG image."""

    @abstractmethod
    def submit_model(self, *, image: bytes) -> str:
        """Start an async image -> 3D (GLB) task. Returns the task id."""

    @abstractmethod
    def submit_comparison_model(
        self, *, image: bytes, model: str, image_as_list: bool, task_settings: dict
    ) -> str:
        """TEMPORARY, for /models-comparison: `submit_model` with any model and settings."""

    @abstractmethod
    def get_model(self, *, task_id: str) -> ModelTask:
        """Current state of a 3D task started by `submit_model`."""

    @abstractmethod
    def get_credits(self) -> AccountCredits:
        """Remaining balance and all-time spend of the provider account."""


@cache
def _resolve(setting_name: str):
    return import_string(getattr(settings, setting_name))()


def reset_ports() -> None:
    _resolve.cache_clear()


def get_generation_port() -> GenerationPort:
    return _resolve("GENERATION_ADAPTER")
