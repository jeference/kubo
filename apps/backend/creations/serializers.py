from __future__ import annotations

from datetime import datetime

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from common.serializers import GlobalIdSerializer
from creations import costing
from creations.fsm import TASK_ACTIVE
from creations.models import Creation, ImageVersion, Model3D, ProviderTask
from media import services as media


class ImageVersionSerializer(GlobalIdSerializer):
    parent_id = serializers.UUIDField(source="parent.globalid", allow_null=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ImageVersion
        fields = [
            "id",
            "number",
            "parent_id",
            "origin",
            "instruction",
            "image_url",
            "has_plain_background",
            "background_lost",
            "created_at",
        ]
        read_only_fields = fields

    def get_image_url(self, version) -> str:
        return media.signed_url(version.asset)


class Model3DSerializer(GlobalIdSerializer):
    glb_url = serializers.SerializerMethodField()
    source_version_id = serializers.UUIDField(source="source_version.globalid", read_only=True)

    class Meta:
        model = Model3D
        fields = ["id", "source_version_id", "glb_url", "triangles", "created_at"]
        read_only_fields = fields

    def get_glb_url(self, model) -> str:
        return media.signed_url(model.asset)


class ProviderTaskSerializer(GlobalIdSerializer):
    source_version_id = serializers.UUIDField(
        source="source_version.globalid", allow_null=True, read_only=True
    )
    is_active = serializers.SerializerMethodField()
    is_refused = serializers.SerializerMethodField()

    class Meta:
        model = ProviderTask
        fields = [
            "id",
            "kind",
            "status",
            "instruction",
            "source_version_id",
            "is_active",
            "is_refused",
            "created_at",
            "finished_at",
        ]
        read_only_fields = fields

    def get_is_active(self, task) -> bool:
        return task.status in TASK_ACTIVE

    def get_is_refused(self, task) -> bool:
        return task.error_code == "content_refused"


class CreationErrorSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()


class CreationListSerializer(GlobalIdSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    text = serializers.CharField(source="input.text", read_only=True)

    class Meta:
        model = Creation
        fields = ["id", "status", "style", "text", "thumbnail_url", "created_at"]
        read_only_fields = fields

    def get_thumbnail_url(self, creation) -> str:
        version = creation.current_version
        return media.signed_url(version.asset) if version else ""


class CreationDetailSerializer(GlobalIdSerializer):
    text = serializers.CharField(source="input.text", read_only=True)
    has_photo = serializers.SerializerMethodField()
    current_version_id = serializers.UUIDField(
        source="current_version.globalid", allow_null=True, read_only=True
    )
    versions = ImageVersionSerializer(many=True, read_only=True)
    model = serializers.SerializerMethodField()
    edit_tasks = serializers.SerializerMethodField()
    error = serializers.SerializerMethodField()
    blocked_size_ids = serializers.SerializerMethodField()
    is_generating = serializers.SerializerMethodField()
    active_started_at = serializers.SerializerMethodField()

    class Meta:
        model = Creation
        fields = [
            "id",
            "status",
            "style",
            "text",
            "has_photo",
            "active_started_at",
            "current_version_id",
            "versions",
            "model",
            "edit_tasks",
            "error",
            "blocked_size_ids",
            "is_generating",
            "created_at",
        ]
        read_only_fields = fields

    def get_has_photo(self, creation) -> bool:
        return creation.input.photo_id is not None

    @extend_schema_field(Model3DSerializer(allow_null=True))
    def get_model(self, creation):
        if creation.current_model_id is None:
            return None
        return Model3DSerializer(creation.current_model).data

    @extend_schema_field(ProviderTaskSerializer(many=True))
    def get_edit_tasks(self, creation):
        tasks = (
            creation.tasks.filter(kind=ProviderTask.Kind.IMAGE_EDIT)
            .select_related("source_version")
            .order_by("-created_at")[:20]
        )
        return ProviderTaskSerializer(tasks, many=True).data

    @extend_schema_field(CreationErrorSerializer(allow_null=True))
    def get_error(self, creation):
        if not creation.last_error_code:
            return None
        return {"code": creation.last_error_code, "message": creation.last_error_message}

    def get_blocked_size_ids(self, creation) -> list[str]:
        from catalog.models import ProductSize

        blocked = costing.blocked_size_ids(creation.current_model)
        return [
            str(value)
            for value in ProductSize.objects.filter(pk__in=blocked).values_list(
                "globalid", flat=True
            )
        ]

    def get_active_started_at(self, creation) -> datetime | None:
        """Início da etapa em andamento: o tempo na tela sobrevive a recarregar a página."""
        task = (
            creation.tasks.filter(status__in=TASK_ACTIVE)
            .exclude(kind=ProviderTask.Kind.IMAGE_EDIT)
            .order_by("-created_at")
            .first()
        )
        return task.created_at if task else None

    def get_is_generating(self, creation) -> bool:
        return creation.tasks.filter(status__in=TASK_ACTIVE).exists()


class CreationCreateSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    style = serializers.CharField(max_length=24)
    photo = serializers.ImageField(required=False, allow_null=True)
    rights_accepted = serializers.BooleanField(required=False, default=False)


class EditRequestSerializer(serializers.Serializer):
    version_id = serializers.UUIDField()
    instruction = serializers.CharField(max_length=200)


class ApplyVersionSerializer(serializers.Serializer):
    version_id = serializers.UUIDField()


class QuotaKindSerializer(serializers.Serializer):
    limit = serializers.IntegerField()
    used = serializers.IntegerField()
    remaining = serializers.IntegerField()


class QuotaSerializer(serializers.Serializer):
    image = QuotaKindSerializer()
    edit = QuotaKindSerializer()
    model = QuotaKindSerializer()
