from django.core.management.base import BaseCommand

from creations.worker import reconcile_stuck_tasks


class Command(BaseCommand):
    help = "Encerra tarefas de IA presas e devolve a cota."

    def handle(self, *args, **options):
        reconcile_stuck_tasks()
