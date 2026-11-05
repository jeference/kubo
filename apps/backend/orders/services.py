"""Carrinho e pedido. O servidor recalcula tudo: preço, bloqueios e frete."""

from __future__ import annotations

import re
import secrets

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from audit.services import record_event
from catalog.models import ProductSize
from common.crypto import encrypt, sha256_hex
from common.exceptions import Conflict, GuardFailed, ResourceNotFound
from common.fsm import apply_transition
from creations import costing
from creations.models import Creation
from creations.services import creations_for
from notifications.services import send_email
from orders.fsm import ORDER_FSM
from orders.models import Address, Cart, CartItem, Order, OrderItem
from shipping import services as shipping
from shipping.models import ShippingQuote

_NUMBER_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
_OPEN_STATUSES = (Order.Status.PAID, Order.Status.IN_PRODUCTION, Order.Status.SHIPPED)


def brl(cents: int) -> str:
    whole = f"{cents // 100:,}".replace(",", ".")
    return f"R$ {whole},{cents % 100:02d}"


# --- Carrinho ---


def _cart_filter(actor) -> dict:
    if actor.user is not None:
        return {"user": actor.user}
    return {"visitor": actor.visitor, "user__isnull": True}


def get_or_create_cart(actor) -> Cart:
    cart = Cart.objects.filter(**_cart_filter(actor)).first()
    if cart is not None:
        return cart
    try:
        with transaction.atomic():
            return Cart.objects.create(**actor.owner_fields())
    except IntegrityError:
        return Cart.objects.get(**_cart_filter(actor))


def cart_items(actor):
    return CartItem.objects.filter(
        cart__in=Cart.objects.filter(**_cart_filter(actor))
    ).select_related("creation", "creation__current_version__asset", "model", "size")


def unavailable_reason(item: CartItem) -> str:
    """Motivo pelo qual o item não pode ser comprado agora. Vazio se pode."""
    if item.creation.deleted_at is not None:
        return "Esta criação foi excluída."
    if item.model.discarded_at is not None or item.creation.current_model_id != item.model_id:
        return "Esta criação foi alterada. Gere o 3D de novo para comprar."
    if not item.size.is_active:
        return "Este tamanho não está mais disponível."
    if item.size_id in costing.blocked_size_ids(item.model):
        return "Este tamanho não está disponível para este modelo."
    return ""


def add_item(*, actor, creation_id, size_id, quantity: int) -> CartItem:
    creation = (
        creations_for(actor).select_related("current_model").filter(globalid=creation_id).first()
    )
    if creation is None:
        raise ResourceNotFound("Criação não encontrada.")
    if creation.status != Creation.Status.READY or creation.current_model is None:
        raise GuardFailed("Esta criação ainda não está pronta.", code="creation_not_ready")
    size = ProductSize.objects.filter(globalid=size_id, is_active=True).first()
    if size is None:
        raise ResourceNotFound("Tamanho não encontrado.")
    if size.pk in costing.blocked_size_ids(creation.current_model):
        raise GuardFailed("Este tamanho não está disponível para este modelo.", code="size_blocked")
    limit = settings.BUSINESS["MAX_ITEM_QUANTITY"]
    if not 1 <= quantity <= limit:
        raise GuardFailed(f"A quantidade deve ser de 1 a {limit}.", code="invalid_quantity")
    cart = get_or_create_cart(actor)
    with transaction.atomic():
        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart,
            model=creation.current_model,
            size=size,
            defaults={"creation": creation, "quantity": quantity},
        )
        if not created:
            item.quantity = min(item.quantity + quantity, limit)
            item.save(update_fields=["quantity", "updated_at"])
    return item


def get_item(*, actor, item_id) -> CartItem:
    item = cart_items(actor).filter(globalid=item_id).first()
    if item is None:
        raise ResourceNotFound("Item não encontrado.")
    return item


def update_item(*, actor, item_id, quantity: int) -> CartItem:
    item = get_item(actor=actor, item_id=item_id)
    limit = settings.BUSINESS["MAX_ITEM_QUANTITY"]
    if not 1 <= quantity <= limit:
        raise GuardFailed(f"A quantidade deve ser de 1 a {limit}.", code="invalid_quantity")
    item.quantity = quantity
    item.save(update_fields=["quantity", "updated_at"])
    return item


def remove_item(*, actor, item_id) -> None:
    get_item(actor=actor, item_id=item_id).delete()


def selected_cart_items(*, actor, item_ids) -> list[CartItem]:
    """Itens escolhidos para o checkout. Todos precisam existir e estar disponíveis."""
    items = list(cart_items(actor).filter(globalid__in=item_ids))
    if not items or len(items) != len(set(item_ids)):
        raise GuardFailed("Revise os itens do carrinho.", code="cart_changed")
    for item in items:
        reason = unavailable_reason(item)
        if reason:
            raise GuardFailed(reason, code="item_unavailable")
    return items


def transfer_visitor_cart(*, visitor, user) -> None:
    source = Cart.objects.filter(visitor=visitor, user__isnull=True).first()
    if source is None:
        return
    target = Cart.objects.filter(user=user).first()
    if target is None:
        source.user = user
        source.visitor = None
        source.save(update_fields=["user", "visitor", "updated_at"])
        return
    limit = settings.BUSINESS["MAX_ITEM_QUANTITY"]
    for item in source.items.all():
        existing = target.items.filter(model=item.model, size=item.size).first()
        if existing:
            existing.quantity = min(existing.quantity + item.quantity, limit)
            existing.save(update_fields=["quantity", "updated_at"])
            item.delete()
        else:
            item.cart = target
            item.save(update_fields=["cart", "updated_at"])
    source.delete()


# --- Pedido ---


def _generate_number() -> str:
    return "KB" + "".join(secrets.choice(_NUMBER_ALPHABET) for _ in range(8))


def _valid_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for length in (9, 10):
        total = sum(int(cpf[i]) * (length + 1 - i) for i in range(length))
        digit = (total * 10 % 11) % 10
        if digit != int(cpf[length]):
            return False
    return True


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _resolve_shipping(*, actor, quote_id, postal_code: str, items) -> ShippingQuote:
    """Recota no servidor. Se o valor mudou, o cliente precisa confirmar (RN-15)."""
    previous = ShippingQuote.objects.filter(globalid=quote_id, actor_key=actor.key).first()
    if previous is None:
        raise GuardFailed("Escolha o frete de novo.", code="shipping_quote_invalid")
    if previous.destination_postal_code != postal_code:
        raise GuardFailed("O CEP mudou. Escolha o frete de novo.", code="shipping_quote_invalid")
    fresh = shipping.quote(actor=actor, postal_code=postal_code, items=items)
    match = next((q for q in fresh if q.service_id == previous.service_id), None)
    if match is None:
        raise Conflict(
            "Este frete não está mais disponível. Escolha outra opção.",
            code="shipping_changed",
        )
    if match.price_cents != previous.price_cents:
        raise Conflict(
            "O valor do frete mudou. Confirme o novo valor.",
            code="shipping_changed",
            extra={
                "new_quote_id": str(match.globalid),
                "new_price_cents": match.price_cents,
                "new_delivery_days": match.delivery_days,
            },
        )
    return match


def _save_address(user, values: dict) -> None:
    Address.objects.update_or_create(
        user=user,
        postal_code=values["postal_code"],
        number=values["number"],
        complement=values.get("complement", ""),
        defaults={
            "street": values["street"],
            "neighborhood": values["neighborhood"],
            "city": values["city"],
            "state": values["state"],
        },
    )


def create_order(
    *, actor, idempotency_key: str, data: dict, request_id: str = ""
) -> tuple[Order, bool]:
    """Cria o pedido a partir do carrinho. A mesma chave devolve o mesmo pedido."""
    if not idempotency_key:
        raise GuardFailed("Cabeçalho Idempotency-Key obrigatório.", code="idempotency_key_required")
    existing = Order.objects.filter(actor_key=actor.key, idempotency_key=idempotency_key).first()
    if existing:
        return existing, False
    if not data.get("accept_terms"):
        raise GuardFailed("Aceite os termos para continuar.", code="terms_required")

    cpf = _digits(data["cpf"])
    if not _valid_cpf(cpf):
        raise GuardFailed("Informe um CPF válido.", code="invalid_cpf")
    phone = _digits(data["phone"])
    if len(phone) not in (10, 11):
        raise GuardFailed("Informe um telefone com DDD.", code="invalid_phone")
    postal_code = shipping.normalize_postal_code(data["postal_code"])
    state = data["state"].strip().upper()
    if len(state) != 2:
        raise GuardFailed("Informe a UF com duas letras.", code="invalid_state")

    items = selected_cart_items(actor=actor, item_ids=data["item_ids"])
    quote = _resolve_shipping(
        actor=actor, quote_id=data["shipping_quote_id"], postal_code=postal_code, items=items
    )
    subtotal = sum(item.size.price_cents * item.quantity for item in items)
    token = secrets.token_urlsafe(32)
    address = {
        "postal_code": postal_code,
        "street": data["street"].strip(),
        "number": data["number"].strip(),
        "complement": data.get("complement", "").strip(),
        "neighborhood": data["neighborhood"].strip(),
        "city": data["city"].strip(),
        "state": state,
    }
    try:
        with transaction.atomic():
            order = Order.objects.create(
                number=_generate_number(),
                actor_key=actor.key,
                idempotency_key=idempotency_key,
                customer_email=data["email"].strip().lower(),
                customer_name=data["name"].strip(),
                cpf_encrypted=encrypt(cpf),
                cpf_last_digits=cpf[-2:],
                phone=phone,
                postal_code=postal_code,
                street=address["street"],
                address_number=address["number"],
                complement=address["complement"],
                neighborhood=address["neighborhood"],
                city=address["city"],
                state=state,
                subtotal_cents=subtotal,
                shipping_cents=quote.price_cents,
                total_cents=subtotal + quote.price_cents,
                shipping_service_id=quote.service_id,
                shipping_service_name=quote.service_name,
                shipping_company=quote.company,
                delivery_days=quote.delivery_days,
                terms_version=settings.BUSINESS["TERMS_VERSION"],
                terms_accepted_at=timezone.now(),
                tracking_token_hash=sha256_hex(token),
                tracking_token_encrypted=encrypt(token),
                **actor.owner_fields(),
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    creation=item.creation,
                    version=item.model.source_version,
                    model=item.model,
                    size=item.size,
                    size_label=item.size.label,
                    longest_side_mm=item.size.longest_side_mm,
                    quantity=item.quantity,
                    unit_price_cents=item.size.price_cents,
                    style=item.creation.style,
                    prompt_text=item.creation.input.text,
                )
            if actor.user is not None:
                _save_address(actor.user, address)
            record_event(
                instance=order,
                event="created",
                to_state=order.status,
                actor=actor,
                request_id=request_id,
            )
    except IntegrityError:
        return Order.objects.get(actor_key=actor.key, idempotency_key=idempotency_key), False
    return order, True


def orders_for(actor):
    return Order.objects.filter(actor.owner_filter())


def get_order(*, actor, order_id) -> Order:
    order = orders_for(actor).filter(globalid=order_id).first()
    if order is None:
        raise ResourceNotFound("Pedido não encontrado.")
    return order


def get_order_by_token(token: str) -> Order:
    order = Order.objects.filter(tracking_token_hash=sha256_hex(token)).first()
    if order is None:
        raise ResourceNotFound("Pedido não encontrado.")
    return order


def tracking_url(order: Order) -> str:
    from common.crypto import decrypt

    return f"{settings.CONSUMER_APP_URL}/acompanhar/{decrypt(order.tracking_token_encrypted)}"


def has_open_orders(user) -> bool:
    return Order.objects.filter(user=user, status__in=_OPEN_STATUSES).exists()


def delete_saved_addresses(user) -> None:
    Address.objects.filter(user=user).delete()


def claim_orders_for_user(*, user, visitor) -> int:
    """Só o e-mail verificado dá direito a pedidos antigos (RN-21)."""
    if not user.email_verified:
        return 0
    return Order.objects.filter(customer_email=user.email, user__isnull=True).update(user=user)


def resend_tracking_links(email: str) -> None:
    """Sempre responde o mesmo no endpoint: não revela se o e-mail tem pedidos."""
    orders = Order.objects.filter(customer_email=email.strip().lower()).exclude(
        status__in=(Order.Status.PENDING_PAYMENT, Order.Status.EXPIRED)
    )
    for order in orders.order_by("-created_at")[:5]:
        send_email(
            to=order.customer_email,
            subject=f"Acompanhe seu pedido {order.number} na Kubo",
            template="order_tracking_link",
            context={"number": order.number, "tracking_url": tracking_url(order)},
        )


def send_order_confirmed(order: Order) -> None:
    send_email(
        to=order.customer_email,
        subject=f"Recebemos seu pedido {order.number}",
        template="order_confirmed",
        context={
            "number": order.number,
            "total": brl(order.total_cents),
            "delivery_days": order.delivery_days,
            "tracking_url": tracking_url(order),
        },
    )


def send_status_changed(order: Order) -> None:
    shipment = order.shipments.order_by("-created_at").first()
    send_email(
        to=order.customer_email,
        subject=f"Pedido {order.number}: {order.get_status_display()}",
        template="order_status_changed",
        context={
            "number": order.number,
            "status_label": order.get_status_display(),
            "tracking_code": shipment.tracking_code if shipment else "",
            "tracking_url": tracking_url(order),
        },
    )


def transition_order(
    *, order: Order, event: str, actor=None, request_id: str = "", payload=None, effects=None
) -> Order:
    """Toda mudança de status passa por aqui, e o cliente é avisado do que importa a ele."""

    def _effects():
        if effects is not None:
            effects()
        if event in ("start_production", "ship", "deliver", "refund"):
            transaction.on_commit(lambda: send_status_changed(Order.objects.get(pk=order.pk)))

    return apply_transition(
        instance=order,
        fsm=ORDER_FSM,
        event=event,
        actor=actor,
        request_id=request_id,
        payload=payload,
        effects=_effects,
    )


def clear_paid_items_from_cart(order: Order) -> None:
    """O carrinho permanece até o pagamento (RN-18)."""
    filters = {"visitor": order.visitor} if order.user_id is None else {"user": order.user}
    carts = Cart.objects.filter(**filters)
    for item in order.items.all():
        CartItem.objects.filter(cart__in=carts, model=item.model, size=item.size).delete()
