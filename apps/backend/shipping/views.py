from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from common.actor import actor_from_request
from common.exceptions import ResourceNotFound
from common.permissions import IsActor, IsPublic
from orders.services import selected_cart_items
from shipping import serializers as s
from shipping import services


class ShippingQuoteView(APIView):
    permission_classes = [IsActor]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "shipping_quote"

    @extend_schema(request=s.QuoteRequestSerializer, responses=s.ShippingQuoteSerializer(many=True))
    def post(self, request):
        data = s.QuoteRequestSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        actor = actor_from_request(request)
        items = selected_cart_items(actor=actor, item_ids=data.validated_data["item_ids"])
        quotes = services.quote(
            actor=actor, postal_code=data.validated_data["postal_code"], items=items
        )
        return Response(
            s.ShippingQuoteSerializer(quotes, many=True).data, status=status.HTTP_200_OK
        )


class AddressLookupView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "address_lookup"

    @extend_schema(responses=s.AddressLookupSerializer, auth=[])
    def get(self, request, postal_code: str):
        result = services.lookup_address(postal_code)
        if result is None:
            raise ResourceNotFound("CEP não encontrado.")
        return Response(s.AddressLookupSerializer(result).data)
