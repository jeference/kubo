from django.conf import settings
from rest_framework import serializers


def _style_field() -> serializers.ChoiceField:
    return serializers.ChoiceField(
        choices=list(settings.GENERATION["STYLES"]),
        required=False,
        default=settings.DEFAULT_STYLE,
    )


class GenerateImagesSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1000)
    style = _style_field()


class EditImageSerializer(serializers.Serializer):
    instruction = serializers.CharField(max_length=200)


class ImageFileSerializer(serializers.Serializer):
    # Validated (and normalized) by Pillow in the service layer.
    image = serializers.FileField()
    prompt = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")
    style = _style_field()


class CreateModelSerializer(serializers.Serializer):
    image_id = serializers.UUIDField()


class StoredImageSerializer(serializers.Serializer):
    id = serializers.CharField()
    url = serializers.CharField()
    cost = serializers.FloatField(allow_null=True)
    warning = serializers.CharField()


class ModelStatusSerializer(serializers.Serializer):
    id = serializers.CharField()
    status = serializers.CharField()
    glb_url = serializers.CharField()
    cost = serializers.FloatField(allow_null=True)
    error = serializers.CharField()


class CreditsSerializer(serializers.Serializer):
    """Provider account, in USD."""

    balance = serializers.FloatField()
    total_spent = serializers.FloatField()
