"""Stubs: rodam o produto inteiro sem rede e sem custo.

Palavras no prompt simulam situações difíceis: `__recusar__` (conteúdo recusado) e
`__falhar__` (erro do provedor). O estado do PIX fica no cache, compartilhado entre processos.
"""

from __future__ import annotations

import base64
import io
import random
import time
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from PIL import Image, ImageDraw

from integrations.ports import (
    AddressLookupPort,
    AddressResult,
    ContentRefused,
    GatewayCharge,
    GeneratedImage,
    ImageGenerationPort,
    PaymentGatewayPort,
    ProviderTemporaryError,
    ShippingOption,
    ShippingPort,
)

_PALETTES = [
    ["#e4572e", "#29335c", "#f3a712", "#a8c686"],
    ["#2d6a4f", "#95d5b2", "#ffb703", "#3a0ca3"],
    ["#ef476f", "#118ab2", "#06d6a0", "#073b4c"],
    ["#6d597a", "#e56b6f", "#eaac8b", "#355070"],
]


def _delay(name: str, default: float) -> None:
    seconds = getattr(settings, name, default)
    if seconds:
        time.sleep(seconds)


def _png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _figurine(size: int) -> bytes:
    rng = random.Random()
    body, head, accent, detail = rng.choice(_PALETTES)
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)
    s = size / 10
    draw.ellipse((3 * s, 4.5 * s, 7 * s, 9 * s), fill=body)
    draw.ellipse((3.5 * s, 1.5 * s, 6.5 * s, 4.8 * s), fill=head)
    ear = rng.uniform(0.6, 1.2) * s
    draw.polygon([(3.7 * s, 2.4 * s), (4.1 * s, 2.4 * s - ear), (4.6 * s, 2 * s)], fill=accent)
    draw.polygon([(6.3 * s, 2.4 * s), (5.9 * s, 2.4 * s - ear), (5.4 * s, 2 * s)], fill=accent)
    draw.ellipse((4.2 * s, 2.9 * s, 4.6 * s, 3.3 * s), fill=detail)
    draw.ellipse((5.4 * s, 2.9 * s, 5.8 * s, 3.3 * s), fill=detail)
    draw.ellipse((4 * s, 6 * s, 6 * s, 8.5 * s), fill=accent)
    return _png(image)


def _check_triggers(prompt: str) -> None:
    if "__recusar__" in prompt:
        raise ContentRefused("Conteúdo recusado pelo stub.")
    if "__falhar__" in prompt:
        raise ProviderTemporaryError("Falha simulada pelo stub.")


class StubImageGenerationAdapter(ImageGenerationPort):
    provider = "stub"
    model_name = "stub-image"

    def edit(self, *, image: bytes, prompt: str, size: int) -> GeneratedImage:
        _delay("STUB_IMAGE_SECONDS", 1)
        _check_triggers(prompt)
        return GeneratedImage(data=_figurine(size), cost_usd=0.0)


def _stub_key(external_id: str) -> str:
    return f"stub_pix:{external_id}"


def stub_set_charge_status(external_id: str, status: str) -> None:
    """Usado por `simulate_pix_payment` e pelos testes."""
    cache.set(_stub_key(external_id), status, timeout=7 * 24 * 3600)


class StubPaymentGatewayAdapter(PaymentGatewayPort):
    provider = "stub"

    def create_charge(
        self, *, amount: int, reference: str, description: str, expires_in_seconds: int
    ) -> GatewayCharge:
        external_id = f"pix_stub_{uuid.uuid4().hex}"
        stub_set_charge_status(external_id, "pending")
        qr = Image.new("RGB", (240, 240), "white")
        draw = ImageDraw.Draw(qr)
        rng = random.Random(external_id)
        for x in range(0, 240, 12):
            for y in range(0, 240, 12):
                if rng.random() < 0.5:
                    draw.rectangle((x, y, x + 11, y + 11), fill="black")
        return GatewayCharge(
            external_id=external_id,
            status="pending",
            amount=amount,
            pix_br_code=f"00020126STUB{external_id}",
            pix_qr_base64="data:image/png;base64," + base64.b64encode(_png(qr)).decode(),
            expires_at=timezone.now() + timedelta(seconds=expires_in_seconds),
        )

    def get_charge_status(self, *, external_id: str) -> str:
        return cache.get(_stub_key(external_id), "pending")


class StubShippingAdapter(ShippingPort):
    provider = "stub"

    def quote(self, *, origin_postal_code, destination_postal_code, items):
        if destination_postal_code.startswith("99999"):
            return []
        units = sum(item.quantity for item in items)
        base = 1990 + (int(destination_postal_code[0]) * 200) + (units - 1) * 300
        return [
            ShippingOption("1", "PAC", "Correios", base, 8),
            ShippingOption("2", "SEDEX", "Correios", base + 1500, 3),
        ]


class StubAddressLookupAdapter(AddressLookupPort):
    def lookup(self, *, postal_code: str) -> AddressResult | None:
        if postal_code.startswith("99999"):
            return None
        return AddressResult(
            postal_code=postal_code,
            street="Praça da Sé",
            neighborhood="Sé",
            city="São Paulo",
            state="SP",
        )
