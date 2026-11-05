"""Serializers base: a chave interna nunca é exposta; a API vê `globalid` como `id`."""

from rest_framework import serializers


class GlobalIdSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="globalid", read_only=True)


class DetailResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
