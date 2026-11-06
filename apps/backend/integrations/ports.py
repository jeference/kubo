"""Toda capacidade externa fica atrás de um port. O adapter vem de um caminho em settings,
e os stubs permitem rodar e testar tudo sem rede e sem custo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from functools import cache

from django.conf import settings
from django.utils.module_loading import import_string

# --- Erros de geração: o worker decide o que fazer com cada um ---


class ContentRefused(Exception):
    """O provedor recusou o conteúdo. Não adianta repetir."""


class ProviderTemporaryError(Exception):
    """Timeout, 5xx, limite. Vale tentar de novo."""


class ProviderPermanentError(Exception):
    """Erro definitivo do provedor."""


# --- Geração ---


@dataclass(frozen=True)
class GeneratedImage:
    data: bytes
    cost_usd: float | None = None


class ImageGenerationPort(ABC):
    provider = ""
    model_name = ""

    @abstractmethod
    def edit(self, *, image: bytes, prompt: str, size: int) -> GeneratedImage:
        """Imagem de referência + instrução: transforma a foto do cliente e edita versões."""


# --- Pagamento ---


@dataclass(frozen=True)
class GatewayCharge:
    external_id: str
    status: str  # pending | paid | expired | failed | refunded
    amount: int  # centavos
    pix_br_code: str = ""
    pix_qr_base64: str = ""
    expires_at: datetime | None = None


class PaymentGatewayPort(ABC):
    provider = ""

    @abstractmethod
    def create_charge(
        self, *, amount: int, reference: str, description: str, expires_in_seconds: int
    ) -> GatewayCharge: ...

    @abstractmethod
    def get_charge_status(self, *, external_id: str) -> str: ...


# --- Frete ---


@dataclass(frozen=True)
class ShippingItem:
    id: str
    width_cm: int
    height_cm: int
    length_cm: int
    weight_kg: float
    insurance_cents: int
    quantity: int


@dataclass(frozen=True)
class ShippingOption:
    service_id: str
    service_name: str
    company: str
    price_cents: int
    delivery_days: int


class ShippingPort(ABC):
    provider = ""

    @abstractmethod
    def quote(
        self, *, origin_postal_code: str, destination_postal_code: str, items: list[ShippingItem]
    ) -> list[ShippingOption]: ...

    def refresh_credentials(self) -> None:  # noqa: B027
        """Renova credenciais, para fornecedores com token de validade curta."""


# --- Endereço ---


@dataclass(frozen=True)
class AddressResult:
    postal_code: str
    street: str = ""
    neighborhood: str = ""
    city: str = ""
    state: str = ""


class AddressLookupPort(ABC):
    @abstractmethod
    def lookup(self, *, postal_code: str) -> AddressResult | None: ...


# --- Storage ---


class MediaStoragePort(ABC):
    @abstractmethod
    def put(self, *, key: str, data: bytes, content_type: str) -> None: ...

    @abstractmethod
    def get(self, *, key: str) -> bytes | None: ...

    @abstractmethod
    def delete(self, *, key: str) -> None: ...

    @abstractmethod
    def signed_url(self, *, key: str, ttl_seconds: int, content_type: str = "") -> str: ...


# --- E-mail ---


class EmailPort(ABC):
    @abstractmethod
    def send(self, *, to: str, subject: str, body: str, html_body: str | None = None) -> None: ...


# --- Resolução ---


@cache
def _resolve(setting_name: str):
    return import_string(getattr(settings, setting_name))()


def reset_ports() -> None:
    _resolve.cache_clear()


def get_image_generation_port() -> ImageGenerationPort:
    return _resolve("IMAGE_GENERATION_ADAPTER")


def get_payment_gateway_port() -> PaymentGatewayPort:
    return _resolve("PAYMENT_GATEWAY_ADAPTER")


def get_shipping_port() -> ShippingPort:
    return _resolve("SHIPPING_ADAPTER")


def get_address_lookup_port() -> AddressLookupPort:
    return _resolve("ADDRESS_LOOKUP_ADAPTER")


def get_media_storage_port() -> MediaStoragePort:
    return _resolve("MEDIA_STORAGE_ADAPTER")


def get_email_port() -> EmailPort:
    return _resolve("EMAIL_ADAPTER")
