from __future__ import annotations

from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from common.actor import actor_from_request
from common.http import request_id_of
from common.permissions import IsActor, IsAuthenticatedUser, IsPublic
from common.serializers import DetailResponseSerializer
from common.throttling import EmailScopedRateThrottle
from orders import serializers as s
from orders import services
from orders.models import Address
from payments import services as payments


def _cart_payload(actor) -> dict:
    items = list(services.cart_items(actor))
    available = [item for item in items if not services.unavailable_reason(item)]
    return {
        "items": items,
        "subtotal_cents": sum(item.size.price_cents * item.quantity for item in available),
        "item_count": sum(item.quantity for item in items),
    }


class CartView(APIView):
    permission_classes = [IsActor]

    @extend_schema(responses=s.CartSerializer)
    def get(self, request):
        return Response(s.CartSerializer(_cart_payload(actor_from_request(request))).data)


class CartItemListView(APIView):
    permission_classes = [IsActor]

    @extend_schema(request=s.CartItemCreateSerializer, responses={201: s.CartItemSerializer})
    def post(self, request):
        data = s.CartItemCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        item = services.add_item(actor=actor_from_request(request), **data.validated_data)
        return Response(s.CartItemSerializer(item).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    permission_classes = [IsActor]

    @extend_schema(request=s.CartItemUpdateSerializer, responses=s.CartItemSerializer)
    def patch(self, request, item_id):
        data = s.CartItemUpdateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        item = services.update_item(
            actor=actor_from_request(request),
            item_id=item_id,
            quantity=data.validated_data["quantity"],
        )
        return Response(s.CartItemSerializer(item).data)

    @extend_schema(responses={204: None})
    def delete(self, request, item_id):
        services.remove_item(actor=actor_from_request(request), item_id=item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(get=extend_schema(responses=s.OrderListSerializer(many=True)))
class OrderListView(ListAPIView):
    permission_classes = [IsActor]
    serializer_class = s.OrderListSerializer

    def get_queryset(self):
        return (
            services.orders_for(actor_from_request(self.request))
            .prefetch_related("items")
            .order_by("-created_at")
        )

    def get_throttles(self):
        if self.request.method == "POST":
            self.throttle_scope = "order_write"
            return [ScopedRateThrottle()]
        return []

    @extend_schema(
        request=s.OrderCreateSerializer,
        responses={200: s.OrderDetailSerializer, 201: s.OrderDetailSerializer},
        parameters=[
            OpenApiParameter("Idempotency-Key", str, OpenApiParameter.HEADER, required=True)
        ],
    )
    def post(self, request):
        data = s.OrderCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        order, created = services.create_order(
            actor=actor_from_request(request),
            idempotency_key=request.headers.get("Idempotency-Key", "")[:64],
            data=data.validated_data,
            request_id=request_id_of(request),
        )
        return Response(
            s.OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class OrderDetailView(APIView):
    permission_classes = [IsActor]

    @extend_schema(responses=s.OrderDetailSerializer)
    def get(self, request, order_id):
        order = services.get_order(actor=actor_from_request(request), order_id=order_id)
        return Response(s.OrderDetailSerializer(order).data)


class OrderPayView(APIView):
    permission_classes = [IsActor]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "order_write"

    @extend_schema(request=None, responses=s.OrderDetailSerializer)
    def post(self, request, order_id):
        actor = actor_from_request(request)
        order = services.get_order(actor=actor, order_id=order_id)
        payments.pay_order(order=order, actor=actor, request_id=request_id_of(request))
        order.refresh_from_db()
        return Response(s.OrderDetailSerializer(order).data)


class OrderTrackingView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "order_track"

    @extend_schema(responses=s.OrderTrackingSerializer, auth=[])
    def get(self, request, token: str):
        response = Response(s.OrderTrackingSerializer(services.get_order_by_token(token)).data)
        response["Referrer-Policy"] = "no-referrer"
        return response


class OrderTrackingResendView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]
    throttle_classes = [ScopedRateThrottle, EmailScopedRateThrottle]
    throttle_scope = "order_track_resend"
    email_throttle_scope = "order_track_resend"

    @extend_schema(request=s.ResendTrackingSerializer, responses=DetailResponseSerializer, auth=[])
    def post(self, request):
        data = s.ResendTrackingSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        services.resend_tracking_links(data.validated_data["email"])
        return Response(
            DetailResponseSerializer(
                {"detail": "Se houver pedidos com este e-mail, enviaremos os links."}
            ).data
        )


class AddressListView(APIView):
    permission_classes = [IsAuthenticatedUser]

    @extend_schema(responses=s.AddressSerializer(many=True))
    def get(self, request):
        addresses = Address.objects.filter(user=request.user)[:5]
        return Response(s.AddressSerializer(addresses, many=True).data)
