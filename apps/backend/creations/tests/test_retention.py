from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from accounts.models import Visitor
from conftest import make_ready_creation
from creations.models import Creation
from creations.services import purge_expired_assets
from orders.tests.helpers import place_order


def test_deleted_creation_without_order_is_purged_after_period(visitor_client):
    detail = make_ready_creation(visitor_client)
    creation = Creation.objects.get(globalid=detail["id"])
    Creation.objects.filter(pk=creation.pk).update(deleted_at=timezone.now() - timedelta(days=31))
    # A imagem gerada e a foto enviada.
    assert purge_expired_assets()["generated"] == 2
    creation.current_version.asset.refresh_from_db()
    creation.input.photo.refresh_from_db()
    assert creation.current_version.asset.purged_at is not None
    assert creation.input.photo.purged_at is not None


def test_assets_on_orders_are_never_purged(visitor_client):
    order = place_order(visitor_client)
    from orders.models import OrderItem

    item = OrderItem.objects.get(order__globalid=order["id"])
    Creation.objects.filter(pk=item.creation_id).update(
        deleted_at=timezone.now() - timedelta(days=400),
        created_at=timezone.now() - timedelta(days=400),
    )
    assert purge_expired_assets()["generated"] == 0
    assert item.version.asset.purged_at is None


def test_inactive_visitor_is_removed_and_creation_hidden(visitor_client):
    detail = make_ready_creation(visitor_client)
    Visitor.objects.filter(pk=visitor_client.visitor.pk).update(
        last_seen_at=timezone.now() - timedelta(days=400)
    )
    assert purge_expired_assets()["visitors"] == 1
    assert Creation.objects.get(globalid=detail["id"]).deleted_at is not None
