"""Alertas internos. Não há tela neste app: ficam no log, marcados com `alert=true`."""

from __future__ import annotations

import structlog

log = structlog.get_logger("alerts")


def alert(event: str, **context) -> None:
    log.error(event, alert=True, **context)
