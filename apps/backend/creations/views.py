from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from common.actor import actor_from_request
from common.http import client_ip, hash_ip, request_id_of
from common.permissions import IsActor
from creations import quota, services
from creations import serializers as s


def _context(request):
    return actor_from_request(request), hash_ip(client_ip(request))


def _detail(creation) -> dict:
    fresh = services.get_creation_for_response(creation)
    return s.CreationDetailSerializer(fresh).data


@extend_schema_view(get=extend_schema(responses=s.CreationListSerializer(many=True)))
class CreationListView(ListAPIView):
    permission_classes = [IsActor]
    serializer_class = s.CreationListSerializer

    def get_queryset(self):
        actor = actor_from_request(self.request)
        return (
            services.creations_for(actor)
            .select_related("input", "current_version", "current_version__asset")
            .order_by("-created_at")
        )

    def get_throttles(self):
        if self.request.method == "POST":
            self.throttle_scope = "generation_write"
            return [ScopedRateThrottle()]
        return []

    parser_classes = [MultiPartParser, JSONParser]

    @extend_schema(
        request={"multipart/form-data": s.CreationCreateSerializer},
        responses={202: s.CreationDetailSerializer},
    )
    def post(self, request):
        data = s.CreationCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        actor, ip_hash = _context(request)
        values = data.validated_data
        photo = values.get("photo")
        creation = services.start_creation(
            actor=actor,
            ip_hash=ip_hash,
            text=values.get("text", ""),
            style=values["style"],
            photo_bytes=photo.read() if photo else None,
            rights_accepted=values["rights_accepted"],
            request_id=request_id_of(request),
        )
        return Response(_detail(creation), status=status.HTTP_202_ACCEPTED)


class CreationDetailView(APIView):
    permission_classes = [IsActor]

    @extend_schema(responses=s.CreationDetailSerializer)
    def get(self, request, creation_id):
        creation = services.get_creation(actor_from_request(request), creation_id)
        return Response(_detail(creation))

    @extend_schema(responses={204: None})
    def delete(self, request, creation_id):
        actor = actor_from_request(request)
        creation = services.get_creation(actor, creation_id)
        services.delete_creation(actor=actor, creation=creation, request_id=request_id_of(request))
        return Response(status=status.HTTP_204_NO_CONTENT)


class _WriteActionView(APIView):
    permission_classes = [IsActor]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "generation_write"


class CreationRetryView(_WriteActionView):
    @extend_schema(request=None, responses={202: s.CreationDetailSerializer})
    def post(self, request, creation_id):
        actor, ip_hash = _context(request)
        creation = services.get_creation(actor, creation_id)
        services.retry(
            actor=actor, ip_hash=ip_hash, creation=creation, request_id=request_id_of(request)
        )
        return Response(_detail(creation), status=status.HTTP_202_ACCEPTED)


class CreationEditView(_WriteActionView):
    @extend_schema(request=s.EditRequestSerializer, responses={202: s.CreationDetailSerializer})
    def post(self, request, creation_id):
        data = s.EditRequestSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        actor, ip_hash = _context(request)
        creation = services.get_creation(actor, creation_id)
        services.request_edit(
            actor=actor,
            ip_hash=ip_hash,
            creation=creation,
            instruction=data.validated_data["instruction"],
            version_id=data.validated_data["version_id"],
        )
        return Response(_detail(creation), status=status.HTTP_202_ACCEPTED)


class CreationEditCancelView(APIView):
    permission_classes = [IsActor]

    @extend_schema(request=None, responses=s.CreationDetailSerializer)
    def post(self, request, creation_id, task_id):
        creation = services.get_creation(actor_from_request(request), creation_id)
        services.cancel_edit(creation=creation, task_id=task_id)
        return Response(_detail(creation))


class CreationApplyVersionView(APIView):
    permission_classes = [IsActor]

    @extend_schema(request=s.ApplyVersionSerializer, responses=s.CreationDetailSerializer)
    def post(self, request, creation_id):
        data = s.ApplyVersionSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        actor = actor_from_request(request)
        creation = services.get_creation(actor, creation_id)
        services.apply_version(
            actor=actor,
            creation=creation,
            version_id=data.validated_data["version_id"],
            request_id=request_id_of(request),
        )
        return Response(_detail(creation))


class QuotaView(APIView):
    permission_classes = [IsActor]

    @extend_schema(responses=s.QuotaSerializer)
    def get(self, request):
        return Response(s.QuotaSerializer(quota.usage_for(actor_from_request(request))).data)
