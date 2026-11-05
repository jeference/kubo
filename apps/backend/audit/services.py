from __future__ import annotations

from audit.models import DomainEvent


def record_event(
    *, instance, event: str, from_state="", to_state="", actor=None, payload=None, request_id=""
) -> DomainEvent:
    """Grava um evento para qualquer modelo com `globalid`. `actor`: `Actor`, usuário ou nada."""
    user = getattr(actor, "user", actor)
    visitor = getattr(actor, "visitor", None)
    return DomainEvent.objects.create(
        aggregate_type=instance._meta.label,
        aggregate_id=instance.globalid,
        event=event,
        from_state=from_state,
        to_state=to_state,
        actor_user=user if user is not None and getattr(user, "pk", None) else None,
        actor_label=f"visitor:{visitor.globalid}" if visitor is not None else "",
        payload=payload or {},
        request_id=request_id or "",
    )
