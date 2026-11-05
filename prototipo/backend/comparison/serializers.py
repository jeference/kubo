from django.conf import settings
from rest_framework import serializers


class CreateRunSerializer(serializers.Serializer):
    # Validated (and normalized) by Pillow in the service layer.
    image = serializers.FileField()
    models = serializers.ListField(
        child=serializers.ChoiceField(choices=list(settings.MODEL_COMPARISON)), allow_empty=False
    )


class CatalogModelSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    estimated_cost = serializers.FloatField()
    settings = serializers.DictField()


class RunModelSerializer(CatalogModelSerializer):
    status = serializers.CharField()
    glb_url = serializers.CharField()
    cost = serializers.FloatField(allow_null=True)
    error = serializers.CharField()
    seconds = serializers.IntegerField(allow_null=True)
    triangles = serializers.IntegerField(allow_null=True)
    file_bytes = serializers.IntegerField(allow_null=True)


class RunSerializer(serializers.Serializer):
    id = serializers.CharField()
    image_url = serializers.CharField()
    models = RunModelSerializer(many=True)
