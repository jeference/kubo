"""Serve arquivos do storage local por token assinado. Em produção, a URL é do S3."""

from __future__ import annotations

from django.core import signing
from django.http import Http404, HttpResponse
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.views import APIView

from common.permissions import IsPublic
from integrations.adapters.media_local import SIGNING_SALT
from integrations.ports import get_media_storage_port


class MediaView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]

    @extend_schema(responses={(200, "application/octet-stream"): OpenApiTypes.BINARY}, auth=[])
    def get(self, request, token: str):
        try:
            unverified = signing.loads(token, salt=SIGNING_SALT)
            payload = signing.loads(token, salt=SIGNING_SALT, max_age=unverified["t"])
        except (signing.BadSignature, KeyError, TypeError) as exc:
            raise Http404 from exc
        data = get_media_storage_port().get(key=payload["k"])
        if data is None:
            raise Http404
        response = HttpResponse(data, content_type=payload.get("c") or "application/octet-stream")
        response["Cache-Control"] = "private, max-age=300"
        return response
