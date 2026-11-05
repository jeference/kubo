from django.core.management.base import BaseCommand

from payments.services import reconcile_pending_charges


class Command(BaseCommand):
    help = "Confere no gateway as cobranças pendentes, cobrindo webhooks perdidos."

    def handle(self, *args, **options):
        reconcile_pending_charges()
