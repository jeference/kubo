"""Webhook do gateway. Autentica pelo segredo da URL (ou cabeçalho), em tempo constante.

A assinatura `X-Webhook-Signature` não é conferida: a documentação usa uma chave pública, e
ela não prova nada além do segredo. Decisão em aberto: confirmar com a AbacatePay.
"""

from __future__ import annotations

import hmac

from django.conf import settings
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.http import request_id_of
from common.permissions import IsPublic
from payments.services import ingest_gateway_event


def _valid_secret(secret: str) -> bool:
    expected = settings.ABACATE_PAY_WEBHOOK_SECRET
    return bool(expected) and bool(secret) and hmac.compare_digest(secret, expected)


class AbacatePayWebhookView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]

    @extend_schema(
        request=None,
        responses={200: None},
        auth=[],
        parameters=[OpenApiParameter("webhookSecret", str, OpenApiParameter.QUERY, required=True)],
    )
    def post(self, request):
        secret = request.query_params.get("webhookSecret") or request.headers.get(
            "X-Webhook-Secret", ""
        )
        if not _valid_secret(secret):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        payload = request.data if isinstance(request.data, dict) else {}
        ingest_gateway_event(
            provider="abacatepay", payload=payload, request_id=request_id_of(request)
        )
        return Response(status=status.HTTP_200_OK)
