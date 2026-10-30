from rest_framework import serializers


class GenerateImagesSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1000)


class ImageFileSerializer(serializers.Serializer):
    # Validated (and normalized) by Pillow in the service layer.
    image = serializers.FileField()


class CreateModelSerializer(serializers.Serializer):
    image_id = serializers.UUIDField()


class StoredImageSerializer(serializers.Serializer):
    id = serializers.CharField()
    url = serializers.CharField()
    cost = serializers.FloatField(allow_null=True)


class ModelStatusSerializer(serializers.Serializer):
    id = serializers.CharField()
    status = serializers.CharField()
    glb_url = serializers.CharField()
    cost = serializers.FloatField(allow_null=True)
    error = serializers.CharField()
