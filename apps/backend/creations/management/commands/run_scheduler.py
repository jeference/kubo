"""Agendador simples: roda os comandos idempotentes nas frequências da arquitetura.

Em produção, é o container `scheduler`. Cada comando tem seu próprio tratamento de erro,
então uma falha não derruba os demais.
"""

from __future__ import annotations

import time

import structlog
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import close_old_connections

log = structlog.get_logger(__name__)

_JOBS = [
    ("expire_pending_charges", 60),
    ("reconcile_stuck_tasks", 60),
    ("reconcile_pending_charges", 300),
    ("refresh_shipping_token", 86400),
    ("purge_expired_assets", 86400),
]


class Command(BaseCommand):
    help = "Executa as tarefas agendadas."

    def handle(self, *args, **options):
        next_run = {name: 0.0 for name, _ in _JOBS}
        while True:
            now = time.monotonic()
            for name, interval in _JOBS:
                if now < next_run[name]:
                    continue
                next_run[name] = now + interval
                close_old_connections()
                try:
                    call_command(name)
                except Exception:
                    log.exception("scheduled_job_failed", job=name)
            time.sleep(1)
