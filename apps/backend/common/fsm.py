"""Engine da máquina de estados: uma tabela de transições e uma função transacional.

`apply_transition` executa, em uma transação: bloqueia a linha, resolve a transição, roda o
guard, grava o status, grava o `DomainEvent` imutável e roda os efeitos. Falha em qualquer
passo desfaz tudo. Efeitos externos (e-mail) devem usar `transaction.on_commit`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from django.db import transaction

from common.exceptions import IllegalTransition


@dataclass(frozen=True)
class Transition:
    source: str
    dest: str
    event: str


class FSM:
    def __init__(self, transitions: list[Transition]):
        self._by_key = {(t.source, t.event): t for t in transitions}
        self.events = {t.event for t in transitions}
        self.states = {s for t in transitions for s in (t.source, t.dest)}

    def can(self, current: str, event: str) -> bool:
        return (current, event) in self._by_key

    def resolve(self, current: str, event: str) -> Transition:
        try:
            return self._by_key[(current, event)]
        except KeyError:
            raise IllegalTransition(
                f"Transição '{event}' não permitida a partir de '{current}'."
            ) from None


def apply_transition(
    *,
    instance,
    fsm: FSM,
    event: str,
    actor=None,
    request_id: str = "",
    guard: Callable[[], None] | None = None,
    effects: Callable[[], None] | None = None,
    payload: dict | None = None,
    status_field: str = "status",
):
    """Executa uma transição e devolve a instância atualizada."""
    from audit.services import record_event

    model = instance.__class__
    with transaction.atomic():
        locked = model.objects.select_for_update().get(pk=instance.pk)
        current = getattr(locked, status_field)
        transition = fsm.resolve(current, event)
        if guard is not None:
            guard()
        setattr(locked, status_field, transition.dest)
        locked.save(update_fields=[status_field, "updated_at"])
        record_event(
            instance=locked,
            event=event,
            from_state=current,
            to_state=transition.dest,
            actor=actor,
            payload=payload,
            request_id=request_id,
        )
        if effects is not None:
            effects()
    setattr(instance, status_field, transition.dest)
    return locked
