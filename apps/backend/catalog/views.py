from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog import prompts, serializers
from catalog.models import ProductSize
from common.permissions import IsPublic


class StyleListView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]

    @extend_schema(responses=serializers.StyleSerializer(many=True), auth=[])
    def get(self, request):
        return Response(serializers.StyleSerializer(prompts.public_styles(), many=True).data)


class SizeListView(APIView):
    authentication_classes: list = []
    permission_classes = [IsPublic]

    @extend_schema(responses=serializers.ProductSizeSerializer(many=True), auth=[])
    def get(self, request):
        sizes = ProductSize.objects.filter(is_active=True)
        return Response(serializers.ProductSizeSerializer(sizes, many=True).data)
