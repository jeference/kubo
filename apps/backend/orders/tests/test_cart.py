from __future__ import annotations

from catalog.models import ProductSize
from conftest import creation_payload, drain_worker, make_ready_creation
from orders.tests.helpers import add_to_cart


def test_add_requires_ready_creation(visitor_client):
    creation = visitor_client.post(
        "/api/creations/", creation_payload("a"), format="multipart"
    ).data
    size = visitor_client.get("/api/catalog/sizes/").data[0]
    response = visitor_client.post(
        "/api/cart/items/", {"creation_id": creation["id"], "size_id": size["id"], "quantity": 1}
    )
    assert response.status_code == 422
    assert response.data["code"] == "creation_not_ready"


def test_add_merges_and_totals(visitor_client):
    creation = make_ready_creation(visitor_client)
    add_to_cart(visitor_client, creation=creation, quantity=2)
    add_to_cart(visitor_client, creation=creation, quantity=1)
    cart = visitor_client.get("/api/cart/").data
    assert len(cart["items"]) == 1
    assert cart["item_count"] == 3
    assert cart["subtotal_cents"] == 3 * 9990


def test_quantity_limits(visitor_client):
    item = add_to_cart(visitor_client)
    url = f"/api/cart/items/{item['id']}/"
    assert visitor_client.patch(url, {"quantity": 11}).status_code == 400
    assert visitor_client.patch(url, {"quantity": 0}).status_code == 400
    assert visitor_client.patch(url, {"quantity": 10}).data["quantity"] == 10


def test_remove_item(visitor_client):
    item = add_to_cart(visitor_client)
    assert visitor_client.delete(f"/api/cart/items/{item['id']}/").status_code == 204
    assert visitor_client.get("/api/cart/").data["item_count"] == 0


def test_cart_is_scoped(visitor_client, other_visitor_client):
    item = add_to_cart(visitor_client)
    url = f"/api/cart/items/{item['id']}/"
    assert other_visitor_client.patch(url, {"quantity": 2}).status_code == 404
    assert other_visitor_client.delete(url).status_code == 404
    assert other_visitor_client.get("/api/cart/").data["item_count"] == 0


def test_cannot_add_other_visitors_creation(visitor_client, other_visitor_client):
    creation = make_ready_creation(visitor_client)
    size = other_visitor_client.get("/api/catalog/sizes/").data[0]
    response = other_visitor_client.post(
        "/api/cart/items/", {"creation_id": creation["id"], "size_id": size["id"], "quantity": 1}
    )
    assert response.status_code == 404


def test_inactive_size_makes_item_unavailable(visitor_client):
    item = add_to_cart(visitor_client)
    ProductSize.objects.filter(code="6cm").update(is_active=False)
    cart = visitor_client.get("/api/cart/").data
    assert cart["items"][0]["unavailable_reason"]
    assert cart["subtotal_cents"] == 0
    assert item["id"] == cart["items"][0]["id"]


def test_editing_after_adding_keeps_the_item_and_its_image(visitor_client):
    creation = make_ready_creation(visitor_client)
    item = add_to_cart(visitor_client, creation=creation)
    visitor_client.post(
        f"/api/creations/{creation['id']}/edits/",
        {"version_id": creation["versions"][0]["id"], "instruction": "azul"},
    )
    drain_worker()
    versions = visitor_client.get(f"/api/creations/{creation['id']}/").data["versions"]
    visitor_client.post(
        f"/api/creations/{creation['id']}/apply-version/", {"version_id": versions[1]["id"]}
    )
    cart = visitor_client.get("/api/cart/").data
    assert cart["items"][0]["unavailable_reason"] == ""
    assert cart["subtotal_cents"] == item["line_total_cents"]

    # A nova imagem entra como outro item, no mesmo tamanho.
    add_to_cart(visitor_client, creation=creation)
    assert len(visitor_client.get("/api/cart/").data["items"]) == 2
