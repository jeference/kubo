from django.core.management.base import BaseCommand

from payments.services import expire_pending_charges


class Command(BaseCommand):
    help = "Expira PIX vencidos e os pedidos correspondentes."

    def handle(self, *args, **options):
        expire_pending_charges()
