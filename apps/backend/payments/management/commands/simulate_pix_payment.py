"""Desenvolvimento: simula o pagamento do PIX com o gateway stub, passando pelo mesmo fluxo."""

from django.core.management.base import BaseCommand, CommandError

from integrations.adapters.stubs import stub_set_charge_status
from orders.models import Order
from payments.models import Charge
from payments.services import ingest_gateway_event


class Command(BaseCommand):
    help = "Simula o pagamento ou reembolso de um pedido com o gateway stub."

    def add_arguments(self, parser):
        parser.add_argument("number", help="Número do pedido (KB...)")
        parser.add_argument("--refund", action="store_true")

    def handle(self, *args, **options):
        order = Order.objects.filter(number=options["number"]).first()
        if order is None:
            raise CommandError("Pedido não encontrado.")
        charge = order.charges.order_by("-created_at").first()
        if charge is None or not charge.external_id.startswith("pix_stub_"):
            raise CommandError("Este pedido não tem cobrança do stub.")
        refund = options["refund"]
        if not refund:
            stub_set_charge_status(charge.external_id, "paid")
        event = "transparent.refunded" if refund else "transparent.completed"
        ingest_gateway_event(
            provider="abacatepay",
            payload={
                "id": f"sim_{event}_{charge.globalid}",
                "event": event,
                "data": {"id": charge.external_id},
            },
        )
        charge = Charge.objects.get(pk=charge.pk)
        self.stdout.write(
            f"Cobrança: {charge.status}. Pedido: {Order.objects.get(pk=order.pk).status}"
        )
