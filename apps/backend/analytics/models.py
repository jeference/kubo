from django.db import models


class ProductEvent(models.Model):
    """Eventos do funil que não geram `DomainEvent`. Sem dados pessoais."""

    actor_key = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=48)
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["name", "created_at"])]

    def __str__(self) -> str:
        return self.name
