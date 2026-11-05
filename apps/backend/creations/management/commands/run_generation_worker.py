from __future__ import annotations

import signal
import threading
import time

import structlog
from django.conf import settings
from django.core.management.base import BaseCommand

from creations import worker

log = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Executa as tarefas de geração de IA. Rode um ou mais processos."

    def add_arguments(self, parser):
        parser.add_argument("--threads", type=int, default=settings.BUSINESS["WORKER_THREADS"])
        parser.add_argument("--once", action="store_true", help="Esvazia a fila e sai.")

    def handle(self, *args, **options):
        if options["once"]:
            while worker.run_once():
                pass
            return

        stop = threading.Event()
        signal.signal(signal.SIGINT, lambda *_: stop.set())
        signal.signal(signal.SIGTERM, lambda *_: stop.set())

        def loop() -> None:
            while not stop.is_set():
                worker.close_connections()
                try:
                    if not worker.run_once():
                        time.sleep(0.5)
                except Exception:
                    log.exception("worker_loop_error")
                    time.sleep(2)

        threads = [
            threading.Thread(target=loop, name=f"generation-{index}", daemon=True)
            for index in range(options["threads"])
        ]
        for thread in threads:
            thread.start()
        log.info("worker_started", threads=len(threads))
        while not stop.is_set():
            time.sleep(0.5)
        for thread in threads:
            thread.join(timeout=100)
