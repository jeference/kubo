"""AbacatePay v2, checkout transparente com PIX. A confirmação é do webhook; aqui só criamos a
cobrança e consultamos o status. Valores em centavos. Sem dados do cliente: `customer` é
opcional na API, e só o enviaríamos se a conta ou a nota fiscal exigir."""

from __future__ import annotations

import requests
import structlog
from django.conf import settings
from django.utils.dateparse import parse_datetime

from common.exceptions import UpstreamUnavailable
from integrations.ports import GatewayCharge, PaymentGatewayPort

_TIMEOUT_SECONDS = 30
_DESCRIPTION_MAX = 37

# Só PAID e REDEEMED liquidam. APPROVED e UNDER_DISPUTE nunca: na dúvida, pendente.
_STATUS_MAP = {
    "PENDING": "pending",
    "APPROVED": "pending",
    "UNDER_DISPUTE": "pending",
    "PAID": "paid",
    "REDEEMED": "paid",
    "EXPIRED": "expired",
    "CANCELLED": "failed",
    "FAILED": "failed",
    "REFUNDED": "refunded",
}

log = structlog.get_logger(__name__)


class AbacatePayAdapter(PaymentGatewayPort):
    provider = "abacatepay"

    def __init__(self) -> None:
        self._base_url = settings.ABACATE_PAY_BASE_URL.rstrip("/")
        self._api_key = settings.ABACATE_PAY_API_KEY

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _map_status(self, raw: str) -> str:
        if raw not in _STATUS_MAP:
            log.warning("abacatepay_unknown_status", status=raw)
        return _STATUS_MAP.get(raw, "pending")

    def _data_or_raise(self, response: requests.Response, operation: str) -> dict:
        try:
            response.raise_for_status()
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            log.error("abacatepay_http_error", operation=operation, error=str(exc))
            raise UpstreamUnavailable("Gateway de pagamento indisponível.") from exc
        if body.get("error") or body.get("success") is False:
            log.error("abacatepay_api_error", operation=operation)
            raise UpstreamUnavailable("Gateway de pagamento retornou erro.")
        return body.get("data") or {}

    def create_charge(
        self, *, amount: int, reference: str, description: str, expires_in_seconds: int
    ) -> GatewayCharge:
        payload = {
            "method": "PIX",
            "data": {
                "amount": int(amount),
                "expiresIn": expires_in_seconds,
                "description": description[:_DESCRIPTION_MAX],
                "metadata": {"kind": "order", "reference": reference},
            },
        }
        try:
            response = requests.post(
                f"{self._base_url}/transparents/create",
                json=payload,
                headers=self._headers(),
                timeout=_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            log.error("abacatepay_create_charge_exception", error=str(exc))
            raise UpstreamUnavailable("Gateway de pagamento indisponível.") from exc
        data = self._data_or_raise(response, "create_transparent")
        external_id = str(data.get("id") or "")
        if not external_id:
            raise UpstreamUnavailable("Gateway de pagamento retornou resposta inválida.")
        return GatewayCharge(
            external_id=external_id,
            status=self._map_status(data.get("status", "PENDING")),
            amount=int(amount),
            pix_br_code=data.get("brCode", ""),
            pix_qr_base64=data.get("brCodeBase64", ""),
            expires_at=parse_datetime(data.get("expiresAt") or ""),
        )

    def get_charge_status(self, *, external_id: str) -> str:
        try:
            response = requests.get(
                f"{self._base_url}/transparents/check",
                params={"id": external_id},
                headers=self._headers(),
                timeout=_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            log.error("abacatepay_check_status_exception", error=str(exc))
            raise UpstreamUnavailable("Gateway de pagamento indisponível.") from exc
        data = self._data_or_raise(response, "check_transparent_status")
        return self._map_status(data.get("status", "PENDING"))
