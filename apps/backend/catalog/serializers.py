from rest_framework import serializers

from catalog.models import ProductSize
from common.serializers import GlobalIdSerializer


class StyleSerializer(serializers.Serializer):
    id = serializers.CharField()
    label = serializers.CharField()
    thumbnail = serializers.CharField()


class ProductSizeSerializer(GlobalIdSerializer):
    class Meta:
        model = ProductSize
        fields = ["id", "code", "label", "longest_side_mm", "price_cents", "is_default"]
        read_only_fields = fields
