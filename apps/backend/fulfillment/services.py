from __future__ import annotations

from django.conf import settings

from fulfillment.models import Partner, ProductionJob


def origin_postal_code() -> str:
    partner = Partner.objects.filter(is_internal=True).first()
    return partner.origin_postal_code if partner else settings.INTERNAL_PARTNER_POSTAL_CODE


def create_jobs_for_order(order) -> None:
    """Uma tarefa por item, sem parceiro. Idempotente: pagamento tardio não duplica."""
    for item in order.items.all():
        ProductionJob.objects.get_or_create(order_item=item)


def cancel_jobs_for_order(order) -> None:
    jobs = ProductionJob.objects.filter(order_item__order=order).exclude(
        status__in=(ProductionJob.Status.SHIPPED, ProductionJob.Status.CANCELLED)
    )
    for job in jobs:
        job.status = ProductionJob.Status.CANCELLED
        job.save(update_fields=["status", "updated_at"])
