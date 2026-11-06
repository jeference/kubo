from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from analytics.models import ProductEvent
from common.actor import actor_from_request
from common.permissions import IsPublic

ALLOWED_EVENTS = {
    "page_viewed",
    "prompt_submitted",
    "edit_requested",
    "size_selected",
    "item_added_to_cart",
    "buy_now_clicked",
    "checkout_started",
    "shipping_quoted",
    "pix_generated",
    "pix_copied",
}


class EventSerializer(serializers.Serializer):
    name = serializers.ChoiceField(choices=sorted(ALLOWED_EVENTS))
    properties = serializers.DictField(required=False)


class EventView(APIView):
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "events"

    @extend_schema(request=EventSerializer, responses={204: None})
    def post(self, request):
        data = EventSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        ProductEvent.objects.create(
            actor_key=actor_from_request(request).key,
            name=data.validated_data["name"],
            properties=data.validated_data.get("properties", {}),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
