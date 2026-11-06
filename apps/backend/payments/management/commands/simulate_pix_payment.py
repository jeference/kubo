"""Desenvolvimento: simula o pagamento do PIX de um pedido pelo caminho real.

O comando existe só para não gastar dinheiro de verdade. Fora isso ele reflete a produção e
não liquida nada localmente: dispara o simulate-payment do AbacatePay (devMode), o AbacatePay
chama o webhook registrado no painel, e é o webhook (`payments.views`) que confere o status,
lança no ledger e avança o pedido. O comando só espera esse efeito aparecer no banco.

Se o webhook não chega, o comando falha, e a falha é verdadeira: em produção aquele pagamento
também não seria reconhecido. Exige o túnel de pé (`make backend-tunnel`).

    manage.py simulate_pix_payment KB...
"""

from __future__ import annotations

import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from integrations.ports import get_payment_gateway_port
from orders.models import Order
from payments.models import Charge, WebhookEvent

_POLL_SECONDS = 2
_DEFAULT_TIMEOUT_SECONDS = 60


class Command(BaseCommand):
    help = "Simula o pagamento do PIX no AbacatePay (devMode) e espera o webhook liquidar."

    def add_arguments(self, parser):
        parser.add_argument("number", help="Número do pedido (KB...)")
        parser.add_argument(
            "--timeout",
            type=int,
            default=_DEFAULT_TIMEOUT_SECONDS,
            help="Segundos de espera pelo webhook (padrão: %(default)s).",
        )

    def handle(self, *args, **options):
        order = Order.objects.filter(number=options["number"]).first()
        if order is None:
            raise CommandError("Pedido não encontrado.")
        charge = order.charges.order_by("-created_at").first()
        if charge is None:
            raise CommandError("Este pedido não tem cobrança. Gere o PIX pelo app.")

        self.stdout.write(self.style.SUCCESS(f"Cobrança: {charge.globalid}"))
        self.stdout.write(f"  Valor:       R$ {charge.amount_cents / 100:.2f}")
        self.stdout.write(f"  Status:      {charge.get_status_display()}")
        self.stdout.write(f"  external_id: {charge.external_id}")

        if charge.status == Charge.Status.PAID:
            self.stdout.write(self.style.WARNING("A cobrança já está paga, nada a simular."))
            self._report(order, charge)
            return

        since = timezone.now()
        self._simulate_on_gateway(charge)
        self._await_webhook(charge, since=since, timeout=options["timeout"])
        self._report(order, charge)

    def _simulate_on_gateway(self, charge: Charge) -> None:
        if not settings.ABACATE_PAY_API_KEY:
            raise CommandError("ABACATE_PAY_API_KEY não configurada no apps/backend/.env.")
        if charge.provider != "abacatepay":
            raise CommandError(
                f"A cobrança foi criada pelo gateway '{charge.provider}'. Configure "
                "PAYMENT_GATEWAY_ADAPTER com o AbacatePay e gere um novo PIX pelo app."
            )
        simulate = getattr(get_payment_gateway_port(), "simulate_payment", None)
        if simulate is None:
            raise CommandError("O gateway configurado não simula pagamento (use o AbacatePay).")
        self.stdout.write("Disparando o simulate-payment no AbacatePay (devMode)...")
        try:
            data = simulate(external_id=charge.external_id)
        except Exception as exc:  # noqa: BLE001 — ferramenta de dev: mostra a falha real
            raise CommandError(
                f"simulate-payment falhou: {exc}. Confira se a cobrança existe no AbacatePay "
                f"('{charge.external_id}') e se a chave é de devMode."
            ) from exc
        self.stdout.write(self.style.SUCCESS(f"  Gateway respondeu: status={data.get('status')}"))

    def _await_webhook(self, charge: Charge, *, since, timeout: int) -> None:
        """Quem paga a cobrança é o webhook, não este comando: aqui só esperamos."""
        self.stdout.write(f"Aguardando o webhook do AbacatePay (até {timeout}s)...")
        deadline = time.monotonic() + timeout
        while True:
            charge.refresh_from_db()
            if charge.status == Charge.Status.PAID:
                self.stdout.write(self.style.SUCCESS("  Webhook recebido e processado."))
                return
            if time.monotonic() >= deadline:
                raise CommandError(self._timeout_hint(since, timeout))
            time.sleep(_POLL_SECONDS)

    def _timeout_hint(self, since, timeout: int) -> str:
        """Separa "o webhook não chegou" de "chegou e falhou": as causas são diferentes."""
        events = list(
            WebhookEvent.objects.filter(provider="abacatepay", created_at__gte=since).order_by(
                "created_at"
            )
        )
        if not events:
            return (
                f"O webhook não chegou em {timeout}s. Em produção este pagamento também não "
                "seria reconhecido. Confira: o túnel está de pé (make backend-tunnel)? O "
                "webhook está registrado no painel do AbacatePay em "
                "<url do túnel>/api/webhooks/abacatepay/?webhookSecret=<segredo>, com o "
                "evento transparent.completed? O segredo é o mesmo do "
                "ABACATE_PAY_WEBHOOK_SECRET? O host do túnel está em DJANGO_ALLOWED_HOSTS?"
            )
        received = "; ".join(f"{e.event_kind}={e.status} {e.error}".strip() for e in events)
        return (
            f"O webhook chegou mas não liquidou a cobrança em {timeout}s. "
            f"Eventos recebidos: {received}"
        )

    def _report(self, order: Order, charge: Charge) -> None:
        order.refresh_from_db()
        charge.refresh_from_db()
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Pronto."))
        self.stdout.write(f"  Cobrança: {charge.get_status_display()}")
        self.stdout.write(f"  Pedido:   {order.status}")
