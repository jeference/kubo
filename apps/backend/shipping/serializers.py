from rest_framework import serializers

from common.serializers import GlobalIdSerializer
from shipping.models import ShippingQuote


class QuoteRequestSerializer(serializers.Serializer):
    postal_code = serializers.CharField(max_length=9)
    item_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)


class ShippingQuoteSerializer(GlobalIdSerializer):
    class Meta:
        model = ShippingQuote
        fields = [
            "id",
            "service_name",
            "company",
            "price_cents",
            "shipping_days",
            "delivery_days",
            "expires_at",
        ]
        read_only_fields = fields


class AddressLookupSerializer(serializers.Serializer):
    postal_code = serializers.CharField()
    street = serializers.CharField(allow_blank=True)
    neighborhood = serializers.CharField(allow_blank=True)
    city = serializers.CharField(allow_blank=True)
    state = serializers.CharField(allow_blank=True)
