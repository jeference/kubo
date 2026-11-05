from django.conf import settings
from django.db import models

from common.models import AppendOnlyModel


class DomainEvent(AppendOnlyModel):
    """Trilha imutável: toda mudança de status de qualquer agregado."""

    aggregate_type = models.CharField(max_length=64)
    aggregate_id = models.UUIDField()
    event = models.CharField(max_length=64)
    from_state = models.CharField(max_length=32, blank=True)
    to_state = models.CharField(max_length=32, blank=True)
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    actor_label = models.CharField(max_length=64, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta(AppendOnlyModel.Meta):
        indexes = [
            models.Index(fields=["aggregate_type", "aggregate_id"]),
            models.Index(fields=["event", "created_at"]),
        ]
