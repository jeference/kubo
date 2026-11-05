"""Cotação de frete por CEP. O prazo mostrado soma a produção ao transporte (RN-16)."""

from __future__ import annotations

import re
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from common.exceptions import GuardFailed
from fulfillment.services import origin_postal_code
from integrations.ports import ShippingItem, get_address_lookup_port, get_shipping_port
from shipping.models import ShippingQuote


def normalize_postal_code(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) != 8:
        raise GuardFailed("Informe um CEP válido.", code="invalid_postal_code")
    return digits


def shipping_items_from_cart(items) -> list[ShippingItem]:
    return [
        ShippingItem(
            id=str(item.globalid),
            width_cm=item.size.package_width_cm,
            height_cm=item.size.package_height_cm,
            length_cm=item.size.package_length_cm,
            weight_kg=item.size.package_weight_grams / 1000,
            insurance_cents=item.size.price_cents * item.quantity,
            quantity=item.quantity,
        )
        for item in items
    ]


def quote(*, actor, postal_code: str, items) -> list[ShippingQuote]:
    """Cota no fornecedor e guarda cada opção. Sem opção, o CEP não é atendido."""
    destination = normalize_postal_code(postal_code)
    origin = origin_postal_code()
    options = get_shipping_port().quote(
        origin_postal_code=origin,
        destination_postal_code=destination,
        items=shipping_items_from_cart(items),
    )
    if not options:
        raise GuardFailed("Ainda não entregamos neste CEP.", code="postal_code_not_served")
    business = settings.BUSINESS
    expires_at = timezone.now() + timedelta(minutes=business["SHIPPING_QUOTE_TTL_MINUTES"])
    return [
        ShippingQuote.objects.create(
            actor_key=actor.key,
            origin_postal_code=origin,
            destination_postal_code=destination,
            service_id=option.service_id,
            service_name=option.service_name,
            company=option.company,
            price_cents=option.price_cents,
            shipping_days=option.delivery_days,
            delivery_days=option.delivery_days + business["PRODUCTION_DAYS"],
            item_ids=[str(item.globalid) for item in items],
            expires_at=expires_at,
        )
        for option in options
    ]


def lookup_address(postal_code: str):
    return get_address_lookup_port().lookup(postal_code=normalize_postal_code(postal_code))


def refresh_credentials() -> None:
    get_shipping_port().refresh_credentials()
