"""Modelos base: chave interna para FK e `globalid` (UUID) exposto na API como `id`."""

import uuid

from django.db import models

from common.exceptions import ImmutableRecordError


class BaseModel(models.Model):
    globalid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.globalid})"


class AppendOnlyModel(BaseModel):
    """Só inserção: correções são lançamentos compensatórios, nunca update ou delete."""

    class Meta(BaseModel.Meta):
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ImmutableRecordError(f"{self.__class__.__name__} é append-only.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ImmutableRecordError(f"{self.__class__.__name__} é append-only.")
