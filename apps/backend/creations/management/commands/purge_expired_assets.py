from django.core.management.base import BaseCommand

from creations.services import purge_expired_assets


class Command(BaseCommand):
    help = "Aplica os prazos de retenção de arquivos."

    def handle(self, *args, **options):
        self.stdout.write(str(purge_expired_assets()))
