"""Uma criação: a entrada do cliente, as versões de imagem e cada tarefa de IA."""

from django.conf import settings
from django.db import models

from common.models import BaseModel


class Creation(BaseModel):
    class Status(models.TextChoices):
        GENERATING_IMAGE = "generating_image", "Gerando imagem"
        IMAGE_FAILED = "image_failed", "Falha na imagem"
        READY = "ready", "Pronta para comprar"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="creations",
    )
    visitor = models.ForeignKey(
        "accounts.Visitor",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="creations",
    )
    status = models.CharField(
        max_length=24, choices=Status.choices, default=Status.GENERATING_IMAGE
    )
    style = models.CharField(max_length=24)
    current_version = models.ForeignKey(
        "creations.ImageVersion", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    last_error_code = models.CharField(max_length=32, blank=True)
    last_error_message = models.CharField(max_length=255, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=["user", "-created_at"])]


class CreationInput(BaseModel):
    creation = models.OneToOneField(Creation, on_delete=models.CASCADE, related_name="input")
    text = models.TextField(blank=True)
    photo = models.ForeignKey(
        "media.Asset", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    rights_accepted_at = models.DateTimeField(null=True, blank=True)
    rights_accepted_ip_hash = models.CharField(max_length=64, blank=True)
    terms_version = models.CharField(max_length=16, blank=True)


class ProviderTask(BaseModel):
    """Uma chamada a um provedor de IA. É também a fila do worker."""

    class Kind(models.TextChoices):
        TEXT_TO_IMAGE = "text_to_image", "Texto para imagem"
        PHOTO_TO_IMAGE = "photo_to_image", "Foto para imagem"
        IMAGE_EDIT = "image_edit", "Edição de imagem"

    class Status(models.TextChoices):
        QUEUED = "queued", "Na fila"
        RUNNING = "running", "Em execução"
        SUCCEEDED = "succeeded", "Concluída"
        FAILED = "failed", "Falhou"
        CANCELLED = "cancelled", "Cancelada"

    creation = models.ForeignKey(Creation, on_delete=models.CASCADE, related_name="tasks")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    source_version = models.ForeignKey(
        "creations.ImageVersion", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    instruction = models.CharField(max_length=255, blank=True)
    provider = models.CharField(max_length=32, blank=True)
    model_name = models.CharField(max_length=64, blank=True)
    rendered_prompt = models.TextField(blank=True)
    prompt_version = models.CharField(max_length=16, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    locked_until = models.DateTimeField(null=True, blank=True)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=32, blank=True)
    error_message = models.CharField(max_length=500, blank=True)

    class Meta(BaseModel.Meta):
        indexes = [models.Index(fields=["status", "next_attempt_at"])]


class ImageVersion(BaseModel):
    class Origin(models.TextChoices):
        TEXT = "text", "Texto"
        PHOTO = "photo", "Foto"
        EDIT = "edit", "Edição"

    creation = models.ForeignKey(Creation, on_delete=models.CASCADE, related_name="versions")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    number = models.PositiveSmallIntegerField()
    origin = models.CharField(max_length=8, choices=Origin.choices)
    instruction = models.CharField(max_length=255, blank=True)
    asset = models.ForeignKey("media.Asset", on_delete=models.PROTECT, related_name="+")
    task = models.ForeignKey(
        ProviderTask, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    has_plain_background = models.BooleanField(default=True)
    background_lost = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(fields=["creation", "number"], name="version_number_uq")
        ]


class QuotaReservation(BaseModel):
    """Cota reservada ao iniciar e consumida só no sucesso (RN-02)."""

    class Kind(models.TextChoices):
        IMAGE = "image", "Geração 2D"
        EDIT = "edit", "Edição"

    class State(models.TextChoices):
        RESERVED = "reserved", "Reservada"
        CONSUMED = "consumed", "Consumida"
        RELEASED = "released", "Liberada"

    actor_key = models.CharField(max_length=32)
    ip_hash = models.CharField(max_length=64, blank=True)
    kind = models.CharField(max_length=8, choices=Kind.choices)
    day = models.DateField()
    state = models.CharField(max_length=10, choices=State.choices, default=State.RESERVED)
    task = models.OneToOneField(
        ProviderTask, on_delete=models.CASCADE, related_name="quota_reservation"
    )

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=["actor_key", "kind", "day"]),
            models.Index(fields=["ip_hash", "kind", "day"]),
        ]
