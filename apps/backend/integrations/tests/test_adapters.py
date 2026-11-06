"""Adapters reais, com as respostas documentadas pelos fornecedores simuladas (sem rede)."""

from __future__ import annotations

import base64
import json

import pytest
import requests
import responses

from common.exceptions import ServiceBusy, UpstreamUnavailable
from integrations.adapters.abacatepay import AbacatePayAdapter
from integrations.adapters.melhor_envio import MelhorEnvioAdapter
from integrations.adapters.runware import RunwareImageGenerationAdapter
from integrations.adapters.viacep import ViaCepAdapter
from integrations.models import IntegrationCredential
from integrations.ports import (
    ContentRefused,
    ProviderPermanentError,
    ProviderTemporaryError,
    ShippingItem,
)

RUNWARE = "https://api.runware.ai/v1"
PNG = base64.b64encode(b"imagem").decode()


@pytest.fixture
def _keys(settings):
    settings.RUNWARE_API_KEY = "chave"
    settings.ABACATE_PAY_API_KEY = "chave"
    settings.ABACATE_PAY_BASE_URL = "https://api.abacatepay.com/v2"
    settings.MELHOR_ENVIO_ACCESS_TOKEN = "token"
    settings.MELHOR_ENVIO_REFRESH_TOKEN = "refresh"
    settings.MELHOR_ENVIO_BASE_URL = "https://sandbox.melhorenvio.com.br"


# --- Runware ---


@responses.activate
def test_runware_edit_returns_bytes_and_cost(_keys):
    responses.post(
        RUNWARE,
        json={"data": [{"imageDataURI": f"data:image/png;base64,{PNG}", "cost": 0.015}]},
    )
    result = RunwareImageGenerationAdapter().edit(image=b"foto", prompt="um gato", size=1024)
    assert result.data == b"imagem"
    assert result.cost_usd == 0.015
    body = json.loads(responses.calls[0].request.body)[0]
    assert body["taskType"] == "imageInference"
    assert body["positivePrompt"] == "um gato"
    assert responses.calls[0].request.headers["Authorization"] == "Bearer chave"


@responses.activate
def test_runware_edit_sends_reference_image(_keys):
    responses.post(RUNWARE, json={"data": [{"imageDataURI": f"data:image/png;base64,{PNG}"}]})
    RunwareImageGenerationAdapter().edit(image=b"foto", prompt="azul", size=1024)
    body = json.loads(responses.calls[0].request.body)[0]
    assert body["inputs"]["referenceImages"][0].startswith("data:image/png;base64,")


@responses.activate
def test_runware_refusal_becomes_content_refused(_keys):
    responses.post(
        RUNWARE,
        json={"data": [], "errors": [{"code": "x", "message": "Rejected by the safety system"}]},
    )
    with pytest.raises(ContentRefused):
        RunwareImageGenerationAdapter().edit(image=b"foto", prompt="x", size=1024)


@responses.activate
def test_runware_other_error_is_permanent(_keys):
    responses.post(
        RUNWARE, json={"data": [], "errors": [{"code": "x", "message": "Invalid model"}]}
    )
    with pytest.raises(ProviderPermanentError):
        RunwareImageGenerationAdapter().edit(image=b"foto", prompt="x", size=1024)


@responses.activate
def test_runware_network_and_5xx_are_temporary(_keys):
    responses.post(RUNWARE, body=requests.ConnectionError("fora"))
    with pytest.raises(ProviderTemporaryError):
        RunwareImageGenerationAdapter().edit(image=b"foto", prompt="x", size=1024)
    responses.replace(responses.POST, RUNWARE, json={"data": []}, status=503)
    with pytest.raises(ProviderTemporaryError):
        RunwareImageGenerationAdapter().edit(image=b"foto", prompt="x", size=1024)


@responses.activate
def test_runware_missing_image_is_permanent(_keys):
    responses.post(RUNWARE, json={"data": [{}]})
    with pytest.raises(ProviderPermanentError):
        RunwareImageGenerationAdapter().edit(image=b"foto", prompt="x", size=1024)


# --- AbacatePay ---

ABACATE = "https://api.abacatepay.com/v2"


@responses.activate
def test_abacatepay_create_charge(_keys):
    responses.post(
        f"{ABACATE}/transparents/create",
        json={
            "data": {
                "id": "pix_char_1",
                "status": "PENDING",
                "brCode": "000201",
                "brCodeBase64": "data:image/png;base64,abc",
                "expiresAt": "2026-11-04T12:00:00Z",
            },
            "success": True,
            "error": None,
        },
    )
    charge = AbacatePayAdapter().create_charge(
        amount=12990, reference="ref", description="Pedido Kubo KB123", expires_in_seconds=1800
    )
    assert charge.external_id == "pix_char_1"
    assert charge.status == "pending"
    assert charge.pix_br_code == "000201"
    body = json.loads(responses.calls[0].request.body)
    assert body["method"] == "PIX"
    assert body["data"]["amount"] == 12990
    assert "customer" not in body["data"]


@pytest.mark.parametrize(
    ("raw", "mapped"),
    [
        ("PAID", "paid"),
        ("REDEEMED", "paid"),
        ("APPROVED", "pending"),
        ("UNDER_DISPUTE", "pending"),
        ("EXPIRED", "expired"),
        ("REFUNDED", "refunded"),
        ("NOVO_STATUS", "pending"),
    ],
)
@responses.activate
def test_abacatepay_only_paid_settles(_keys, raw, mapped):
    responses.get(f"{ABACATE}/transparents/check", json={"data": {"status": raw}, "success": True})
    assert AbacatePayAdapter().get_charge_status(external_id="pix") == mapped


@responses.activate
def test_abacatepay_errors_are_upstream_unavailable(_keys):
    responses.post(f"{ABACATE}/transparents/create", json={"error": "x", "success": False})
    with pytest.raises(UpstreamUnavailable):
        AbacatePayAdapter().create_charge(
            amount=1, reference="r", description="d", expires_in_seconds=1
        )
    responses.get(f"{ABACATE}/transparents/check", status=500)
    with pytest.raises(UpstreamUnavailable):
        AbacatePayAdapter().get_charge_status(external_id="pix")


# --- Melhor Envio ---

CALCULATE = "https://sandbox.melhorenvio.com.br/api/v2/me/shipment/calculate"
ITEM = ShippingItem("i", 12, 10, 12, 0.15, 12990, 2)


@responses.activate
def test_melhor_envio_uses_custom_values_and_skips_errors(_keys):
    responses.post(
        CALCULATE,
        json=[
            {
                "id": 2,
                "name": "SEDEX",
                "price": "40.00",
                "custom_price": "35.50",
                "custom_delivery_time": 3,
                "delivery_time": 2,
                "company": {"name": "Correios"},
            },
            {"id": 3, "name": "Jadlog", "error": "Sem atendimento"},
            {
                "id": 1,
                "name": "PAC",
                "custom_price": "20.10",
                "custom_delivery_time": 8,
                "company": {"name": "Correios"},
            },
        ],
    )
    options = MelhorEnvioAdapter().quote(
        origin_postal_code="01001000", destination_postal_code="01310100", items=[ITEM]
    )
    assert [option.service_name for option in options] == ["PAC", "SEDEX"]
    assert options[0].price_cents == 2010
    assert options[1].delivery_days == 3
    request = responses.calls[0].request
    assert request.headers["Authorization"] == "Bearer token"
    assert "User-Agent" in request.headers
    body = json.loads(request.body)
    assert body["from"]["postal_code"] == "01001000"
    assert body["products"][0]["insurance_value"] == 129.9
    assert body["products"][0]["quantity"] == 2


@responses.activate
def test_melhor_envio_invalid_cep_returns_no_options(_keys):
    responses.post(CALCULATE, json={"message": "invalid"}, status=422)
    assert (
        MelhorEnvioAdapter().quote(
            origin_postal_code="1", destination_postal_code="2", items=[ITEM]
        )
        == []
    )


@responses.activate
def test_melhor_envio_down_is_service_busy(_keys):
    responses.post(CALCULATE, status=500)
    with pytest.raises(ServiceBusy) as error:
        MelhorEnvioAdapter().quote(
            origin_postal_code="1", destination_postal_code="2", items=[ITEM]
        )
    assert error.value.code == "shipping_unavailable"


@responses.activate
def test_melhor_envio_refresh_stores_encrypted_and_is_used(_keys):
    responses.post(
        "https://sandbox.melhorenvio.com.br/oauth/token",
        json={"access_token": "novo", "refresh_token": "novo-refresh", "expires_in": 2592000},
    )
    MelhorEnvioAdapter().refresh_credentials()
    stored = IntegrationCredential.objects.get(provider="melhor_envio")
    assert "novo" not in stored.access_token_encrypted
    responses.post(CALCULATE, json=[])
    MelhorEnvioAdapter().quote(origin_postal_code="1", destination_postal_code="2", items=[ITEM])
    assert responses.calls[1].request.headers["Authorization"] == "Bearer novo"


# --- ViaCEP ---


@responses.activate
def test_viacep():
    responses.get(
        "https://viacep.com.br/ws/01001000/json/",
        json={"logradouro": "Praça da Sé", "bairro": "Sé", "localidade": "São Paulo", "uf": "SP"},
    )
    assert ViaCepAdapter().lookup(postal_code="01001000").city == "São Paulo"
    responses.get("https://viacep.com.br/ws/99999999/json/", json={"erro": "true"})
    assert ViaCepAdapter().lookup(postal_code="99999999") is None
