from django.db import models

from common.models import BaseModel


class EmailLog(BaseModel):
    class Status(models.TextChoices):
        SENT = "sent", "Enviado"
        FAILED = "failed", "Falhou"

    to_hash = models.CharField(max_length=64)
    template = models.CharField(max_length=64)
    status = models.CharField(max_length=12, choices=Status.choices)
    error = models.TextField(blank=True)
