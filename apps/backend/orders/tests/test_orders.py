from __future__ import annotations

import uuid

from catalog.models import ProductSize
from creations.models import CostEstimate
from orders.models import Address, Order
from orders.tests.helpers import add_to_cart, order_payload, place_order, post_order, quote_for


def test_create_order_freezes_values_and_masks_cpf(visitor_client):
    item = add_to_cart(visitor_client, quantity=2)
    quote = quote_for(visitor_client, [item["id"]])[0]
    response = post_order(visitor_client, order_payload([item["id"]], quote["id"]))
    assert response.status_code == 201, response.data
    data = response.data
    assert data["status"] == "pending_payment"
    assert data["subtotal_cents"] == 2 * 9990
    assert data["shipping_cents"] == quote["price_cents"]
    assert data["total_cents"] == 2 * 9990 + quote["price_cents"]
    assert data["delivery_days"] == quote["delivery_days"]
    assert data["cpf_masked"] == "***.***.***-25"
    assert "cpf" not in data
    order = Order.objects.get(globalid=data["id"])
    assert "52998224725" not in order.cpf_encrypted
    assert order.items.get().prompt_text == "um dragão azul"

    ProductSize.objects.filter(code="6cm").update(price_cents=1)
    assert visitor_client.get(f"/api/orders/{data['id']}/").data["subtotal_cents"] == 2 * 9990


def test_idempotency_returns_same_order(visitor_client):
    item = add_to_cart(visitor_client)
    quote = quote_for(visitor_client, [item["id"]])[0]
    payload = order_payload([item["id"]], quote["id"])
    key = uuid.uuid4().hex
    first = post_order(visitor_client, payload, key=key)
    second = post_order(visitor_client, payload, key=key)
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.data["id"] == second.data["id"]
    assert Order.objects.count() == 1


def test_idempotency_key_is_required(visitor_client):
    item = add_to_cart(visitor_client)
    quote = quote_for(visitor_client, [item["id"]])[0]
    response = visitor_client.post(
        "/api/orders/", order_payload([item["id"]], quote["id"]), format="json"
    )
    assert response.status_code == 422
    assert response.data["code"] == "idempotency_key_required"


def test_validations(visitor_client):
    item = add_to_cart(visitor_client)
    quote = quote_for(visitor_client, [item["id"]])[0]
    base = ([item["id"]], quote["id"])
    cases = [
        ({"cpf": "11111111111"}, "invalid_cpf"),
        ({"cpf": "52998224724"}, "invalid_cpf"),
        ({"phone": "123"}, "invalid_phone"),
        ({"accept_terms": False}, "terms_required"),
        ({"postal_code": "02000-000"}, "shipping_quote_invalid"),
    ]
    for overrides, code in cases:
        response = post_order(visitor_client, order_payload(*base, **overrides))
        assert response.data.get("code") == code, (overrides, response.data)


def test_shipping_changed_requires_confirmation(visitor_client, monkeypatch):
    item = add_to_cart(visitor_client)
    quote = quote_for(visitor_client, [item["id"]])[0]
    from integrations.adapters.stubs import StubShippingAdapter
    from integrations.ports import ShippingOption

    class Pricier(StubShippingAdapter):
        def quote(self, *, origin_postal_code, destination_postal_code, items):
            return [ShippingOption("1", "PAC", "Correios", 9999, 8)]

    monkeypatch.setattr("shipping.services.get_shipping_port", lambda: Pricier())
    response = post_order(visitor_client, order_payload([item["id"]], quote["id"]))
    assert response.status_code == 409
    assert response.data["code"] == "shipping_changed"
    assert response.data["new_price_cents"] == 9999
    confirmed = post_order(
        visitor_client, order_payload([item["id"]], response.data["new_quote_id"])
    )
    assert confirmed.status_code == 201
    assert confirmed.data["shipping_cents"] == 9999


def test_blocked_size_rejected_at_closing(visitor_client):
    item = add_to_cart(visitor_client)
    quote = quote_for(visitor_client, [item["id"]])[0]
    CostEstimate.objects.filter(size__code="6cm").update(is_blocked=True)
    response = post_order(visitor_client, order_payload([item["id"]], quote["id"]))
    assert response.status_code == 422
    assert response.data["code"] == "item_unavailable"


def test_order_is_scoped(visitor_client, other_visitor_client, user_client):
    order = place_order(visitor_client)
    for client in (other_visitor_client, user_client):
        assert client.get(f"/api/orders/{order['id']}/").status_code == 404
        assert client.post(f"/api/orders/{order['id']}/pay/").status_code == 404
    assert other_visitor_client.get("/api/orders/").data["count"] == 0
    assert visitor_client.get("/api/orders/").data["count"] == 1


def test_account_order_saves_address(user_client, user):
    place_order(user_client)
    address = Address.objects.get(user=user)
    assert address.postal_code == "01310100"
    assert user_client.get("/api/me/addresses/").data[0]["street"] == "Av. Paulista"


def test_tracking_link_shows_only_masked_data(visitor_client, anon):
    order = place_order(visitor_client)
    from common.crypto import decrypt

    token = decrypt(Order.objects.get(globalid=order["id"]).tracking_token_encrypted)
    response = anon.get(f"/api/orders/track/{token}/")
    assert response.status_code == 200
    assert response.data["number"] == order["number"]
    for private in ("customer_email", "cpf_masked", "phone", "street", "charge"):
        assert private not in response.data
    assert anon.get("/api/orders/track/invalido/").status_code == 404


def test_resend_tracking_does_not_reveal_email(anon):
    unknown = anon.post("/api/orders/track/resend/", {"email": "ninguem@exemplo.com"})
    assert unknown.status_code == 200


def test_shipping_not_served(visitor_client):
    item = add_to_cart(visitor_client)
    response = visitor_client.post(
        "/api/shipping/quotes/", {"postal_code": "99999000", "item_ids": [item["id"]]}
    )
    assert response.status_code == 422
    assert response.data["code"] == "postal_code_not_served"


def test_invalid_postal_code(visitor_client):
    item = add_to_cart(visitor_client)
    response = visitor_client.post(
        "/api/shipping/quotes/", {"postal_code": "123", "item_ids": [item["id"]]}
    )
    assert response.data["code"] == "invalid_postal_code"


def test_address_lookup(anon):
    assert anon.get("/api/shipping/address/01001000/").data["city"] == "São Paulo"
    assert anon.get("/api/shipping/address/99999000/").status_code == 404
