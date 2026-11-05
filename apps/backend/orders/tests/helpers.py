from __future__ import annotations

import uuid

from conftest import make_ready_creation

CPF_OK = "52998224725"


def add_to_cart(client, *, size_code="6cm", quantity=1, creation=None):
    creation = creation or make_ready_creation(client)
    sizes = client.get("/api/catalog/sizes/").data
    size = next(size for size in sizes if size["code"] == size_code)
    response = client.post(
        "/api/cart/items/",
        {"creation_id": creation["id"], "size_id": size["id"], "quantity": quantity},
    )
    assert response.status_code == 201, response.data
    return response.data


def quote_for(client, item_ids, postal_code="01310100"):
    response = client.post(
        "/api/shipping/quotes/", {"postal_code": postal_code, "item_ids": item_ids}
    )
    assert response.status_code == 200, response.data
    return response.data


def order_payload(item_ids, quote_id, **overrides):
    return {
        "item_ids": item_ids,
        "shipping_quote_id": quote_id,
        "email": "comprador@exemplo.com",
        "name": "Ana Souza",
        "cpf": CPF_OK,
        "phone": "11999998888",
        "postal_code": "01310-100",
        "street": "Av. Paulista",
        "number": "1000",
        "complement": "",
        "neighborhood": "Bela Vista",
        "city": "São Paulo",
        "state": "SP",
        "accept_terms": True,
        **overrides,
    }


def post_order(client, payload, key=None):
    return client.post(
        "/api/orders/", payload, HTTP_IDEMPOTENCY_KEY=key or uuid.uuid4().hex, format="json"
    )


def place_order(client, *, email="comprador@exemplo.com", quantity=1):
    item = add_to_cart(client, quantity=quantity)
    quote = quote_for(client, [item["id"]])[0]
    response = post_order(client, order_payload([item["id"]], quote["id"], email=email))
    assert response.status_code == 201, response.data
    return response.data
