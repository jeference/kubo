"""Offline stand-in for the Runware adapter: exercise the whole UI without spending credits.

Images are drawn with Pillow; the 3D task "finishes" after a few seconds and returns
the textured Duck sample GLB from the Khronos glTF sample assets.
"""

from __future__ import annotations

import io
import random
import time
import uuid

from PIL import Image, ImageDraw

from integrations.ports import AccountCredits, GeneratedImage, GenerationPort, ModelTask

_SAMPLE_GLB_URL = (
    "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/"
    "Models/Duck/glTF-Binary/Duck.glb"
)
_MODEL_SECONDS = 6
_PALETTES = [
    ["#e4572e", "#29335c", "#f3a712", "#a8c686"],
    ["#2d6a4f", "#95d5b2", "#ffb703", "#3a0ca3"],
    ["#ef476f", "#118ab2", "#06d6a0", "#073b4c"],
    ["#6d597a", "#e56b6f", "#eaac8b", "#355070"],
]


def _png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _figurine(size: int, palette: list[str], seed: int) -> bytes:
    rng = random.Random(seed)
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)
    s = size / 10
    body, head, accent, detail = palette
    draw.ellipse((3 * s, 4.5 * s, 7 * s, 9 * s), fill=body)
    draw.ellipse((3.5 * s, 1.5 * s, 6.5 * s, 4.8 * s), fill=head)
    ear = rng.uniform(0.6, 1.2) * s
    draw.polygon([(3.7 * s, 2.4 * s), (4.1 * s, 2.4 * s - ear), (4.6 * s, 2 * s)], fill=accent)
    draw.polygon([(6.3 * s, 2.4 * s), (5.9 * s, 2.4 * s - ear), (5.4 * s, 2 * s)], fill=accent)
    draw.ellipse((4.2 * s, 2.9 * s, 4.6 * s, 3.3 * s), fill=detail)
    draw.ellipse((5.4 * s, 2.9 * s, 5.8 * s, 3.3 * s), fill=detail)
    draw.ellipse((4 * s, 6 * s, 6 * s, 8.5 * s), fill=accent)
    return _png(image)


class StubGenerationAdapter(GenerationPort):
    def __init__(self) -> None:
        self._tasks: dict[str, float] = {}

    def generate_images(self, *, prompt: str, count: int, size: int) -> list[GeneratedImage]:
        time.sleep(1)
        seed = random.randrange(1_000_000)
        return [
            GeneratedImage(data=_figurine(size, _PALETTES[i % len(_PALETTES)], seed + i), cost=0)
            for i in range(count)
        ]

    def edit_image(self, *, image: bytes, prompt: str, size: int) -> GeneratedImage:
        time.sleep(1)
        return GeneratedImage(
            data=_figurine(size, random.choice(_PALETTES), random.randrange(1_000_000)), cost=0
        )

    def submit_model(self, *, image: bytes) -> str:
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = time.monotonic()
        return task_id

    def submit_comparison_model(
        self, *, image: bytes, model: str, image_as_list: bool, task_settings: dict
    ) -> str:
        return self.submit_model(image=image)

    def get_model(self, *, task_id: str) -> ModelTask:
        started = self._tasks.get(task_id)
        if started is None:
            return ModelTask(status="error", error="Tarefa desconhecida.")
        if time.monotonic() - started < _MODEL_SECONDS:
            return ModelTask(status="processing")
        return ModelTask(status="success", file_url=_SAMPLE_GLB_URL, cost=0)

    def get_credits(self) -> AccountCredits:
        return AccountCredits(balance=20.0, total_spent=0.0)
