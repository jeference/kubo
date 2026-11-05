"""Melhor Envio: cotação de frete. A API exige `User-Agent` com nome e e-mail técnico.

Usamos `custom_price` e `custom_delivery_time`, que refletem as condições da conta. O token
OAuth dura 30 dias: fica criptografado no banco e é renovado por `refresh_shipping_token`.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal, InvalidOperation

import requests
import structlog
from django.conf import settings
from django.utils import timezone

from common.crypto import decrypt, encrypt
from common.exceptions import ServiceBusy, UpstreamUnavailable
from integrations.models import IntegrationCredential
from integrations.ports import ShippingOption, ShippingPort

_TIMEOUT_SECONDS = 15
_PROVIDER = "melhor_envio"
log = structlog.get_logger(__name__)


def _credential() -> tuple[str, str]:
    stored = IntegrationCredential.objects.filter(provider=_PROVIDER).first()
    if stored:
        return decrypt(stored.access_token_encrypted), decrypt(stored.refresh_token_encrypted)
    return settings.MELHOR_ENVIO_ACCESS_TOKEN, settings.MELHOR_ENVIO_REFRESH_TOKEN


def _to_cents(value) -> int | None:
    try:
        return int(Decimal(str(value)) * 100)
    except (InvalidOperation, TypeError):
        return None


class MelhorEnvioAdapter(ShippingPort):
    provider = _PROVIDER

    def _base(self) -> str:
        return settings.MELHOR_ENVIO_BASE_URL.rstrip("/")

    def quote(self, *, origin_postal_code, destination_postal_code, items):
        access, _ = _credential()
        payload = {
            "from": {"postal_code": origin_postal_code},
            "to": {"postal_code": destination_postal_code},
            "products": [
                {
                    "id": item.id,
                    "width": item.width_cm,
                    "height": item.height_cm,
                    "length": item.length_cm,
                    "weight": item.weight_kg,
                    "insurance_value": round(item.insurance_cents / 100, 2),
                    "quantity": item.quantity,
                }
                for item in items
            ],
        }
        if settings.MELHOR_ENVIO_SERVICES:
            payload["services"] = settings.MELHOR_ENVIO_SERVICES
        try:
            response = requests.post(
                f"{self._base()}/api/v2/me/shipment/calculate",
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access}",
                    "User-Agent": settings.MELHOR_ENVIO_USER_AGENT,
                },
                timeout=_TIMEOUT_SECONDS,
            )
            if response.status_code == 422:
                log.warning("melhor_envio_invalid_quote", body=response.text[:300])
                return []
            response.raise_for_status()
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            log.error("melhor_envio_quote_failed", error=str(exc))
            raise ServiceBusy(
                "Não conseguimos calcular o frete agora. Tente de novo em instantes.",
                code="shipping_unavailable",
            ) from exc

        options = []
        for entry in body if isinstance(body, list) else []:
            if entry.get("error"):  # Serviço sem atendimento para este CEP.
                continue
            price = _to_cents(entry.get("custom_price") or entry.get("price"))
            days = entry.get("custom_delivery_time") or entry.get("delivery_time")
            if price is None or days is None:
                continue
            options.append(
                ShippingOption(
                    service_id=str(entry.get("id")),
                    service_name=str(entry.get("name", "")),
                    company=str((entry.get("company") or {}).get("name", "")),
                    price_cents=price,
                    delivery_days=int(days),
                )
            )
        return sorted(options, key=lambda option: option.price_cents)

    def refresh_credentials(self) -> None:
        _, refresh = _credential()
        if not refresh:
            log.warning("melhor_envio_no_refresh_token")
            return
        try:
            response = requests.post(
                f"{self._base()}/oauth/token",
                json={
                    "grant_type": "refresh_token",
                    "client_id": settings.MELHOR_ENVIO_CLIENT_ID,
                    "client_secret": settings.MELHOR_ENVIO_CLIENT_SECRET,
                    "refresh_token": refresh,
                },
                headers={
                    "Accept": "application/json",
                    "User-Agent": settings.MELHOR_ENVIO_USER_AGENT,
                },
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise UpstreamUnavailable("Não foi possível renovar o token de frete.") from exc
        IntegrationCredential.objects.update_or_create(
            provider=_PROVIDER,
            defaults={
                "access_token_encrypted": encrypt(body["access_token"]),
                "refresh_token_encrypted": encrypt(body.get("refresh_token", refresh)),
                "expires_at": timezone.now() + timedelta(seconds=int(body.get("expires_in", 0))),
            },
        )
