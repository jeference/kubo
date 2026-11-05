from django.db import models

from common.models import BaseModel


class Asset(BaseModel):
    """Um arquivo no storage. O arquivo pode ser expurgado; o registro permanece."""

    class Kind(models.TextChoices):
        PHOTO = "photo", "Foto do cliente"
        IMAGE = "image", "Imagem gerada"
        MODEL = "model", "Modelo 3D"
        PRODUCTION = "production", "Arquivo de produção"

    key = models.CharField(max_length=255, unique=True)
    kind = models.CharField(max_length=16, choices=Kind.choices)
    mime = models.CharField(max_length=64)
    size_bytes = models.PositiveBigIntegerField()
    sha256 = models.CharField(max_length=64)
    purged_at = models.DateTimeField(null=True, blank=True)
