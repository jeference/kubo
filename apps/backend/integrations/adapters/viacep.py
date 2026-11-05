from __future__ import annotations

import requests
import structlog

from integrations.ports import AddressLookupPort, AddressResult

_TIMEOUT_SECONDS = 5
log = structlog.get_logger(__name__)


class ViaCepAdapter(AddressLookupPort):
    def lookup(self, *, postal_code: str) -> AddressResult | None:
        try:
            response = requests.get(
                f"https://viacep.com.br/ws/{postal_code}/json/", timeout=_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            log.warning("viacep_failed", error=str(exc))
            return None
        if body.get("erro"):
            return None
        return AddressResult(
            postal_code=postal_code,
            street=body.get("logradouro", ""),
            neighborhood=body.get("bairro", ""),
            city=body.get("localidade", ""),
            state=body.get("uf", ""),
        )
