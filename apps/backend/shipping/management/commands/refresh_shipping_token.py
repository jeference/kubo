from django.core.management.base import BaseCommand

from common.alerts import alert
from common.exceptions import DomainError
from shipping.services import refresh_credentials


class Command(BaseCommand):
    help = "Renova a credencial do fornecedor de frete."

    def handle(self, *args, **options):
        try:
            refresh_credentials()
        except DomainError as exc:
            alert("shipping_token_refresh_failed", error=exc.detail)
