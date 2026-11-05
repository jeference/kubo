from django.conf import settings
from django.db import models

from common.models import BaseModel


class Cart(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="+"
    )
    visitor = models.ForeignKey(
        "accounts.Visitor", null=True, blank=True, on_delete=models.CASCADE, related_name="+"
    )

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["user"], condition=models.Q(user__isnull=False), name="cart_user_uq"
            ),
            models.UniqueConstraint(
                fields=["visitor"],
                condition=models.Q(visitor__isnull=False, user__isnull=True),
                name="cart_visitor_uq",
            ),
        ]


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    creation = models.ForeignKey("creations.Creation", on_delete=models.CASCADE, related_name="+")
    model = models.ForeignKey("creations.Model3D", on_delete=models.CASCADE, related_name="+")
    size = models.ForeignKey("catalog.ProductSize", on_delete=models.PROTECT, related_name="+")
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta(BaseModel.Meta):
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(fields=["cart", "model", "size"], name="cart_item_uq")
        ]


class Address(BaseModel):
    """Endereço salvo em uma conta, para preencher o próximo checkout."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses"
    )
    postal_code = models.CharField(max_length=8)
    street = models.CharField(max_length=160)
    number = models.CharField(max_length=20)
    complement = models.CharField(max_length=80, blank=True)
    neighborhood = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=2)

    class Meta(BaseModel.Meta):
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "postal_code", "number", "complement"], name="address_user_uq"
            )
        ]


class Order(BaseModel):
    """Tudo aqui é congelado na compra (RN-17). Mudanças posteriores não alteram o pedido."""

    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Aguardando pagamento"
        PAID = "paid", "Recebido"
        IN_PRODUCTION = "in_production", "Em produção"
        SHIPPED = "shipped", "Enviado"
        DELIVERED = "delivered", "Entregue"
        EXPIRED = "expired", "Expirado"
        REFUNDED = "refunded", "Reembolsado"

    number = models.CharField(max_length=16, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    visitor = models.ForeignKey(
        "accounts.Visitor",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    actor_key = models.CharField(max_length=32)
    idempotency_key = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)

    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=120)
    cpf_encrypted = models.TextField()
    cpf_last_digits = models.CharField(max_length=2)
    phone = models.CharField(max_length=20)

    postal_code = models.CharField(max_length=8)
    street = models.CharField(max_length=160)
    address_number = models.CharField(max_length=20)
    complement = models.CharField(max_length=80, blank=True)
    neighborhood = models.CharField(max_length=80)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=2)

    subtotal_cents = models.PositiveIntegerField()
    shipping_cents = models.PositiveIntegerField()
    total_cents = models.PositiveIntegerField()
    shipping_service_id = models.CharField(max_length=32)
    shipping_service_name = models.CharField(max_length=64)
    shipping_company = models.CharField(max_length=64, blank=True)
    delivery_days = models.PositiveSmallIntegerField()

    terms_version = models.CharField(max_length=16)
    terms_accepted_at = models.DateTimeField()
    tracking_token_hash = models.CharField(max_length=64, unique=True)
    tracking_token_encrypted = models.TextField()

    paid_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["actor_key", "idempotency_key"], name="order_idempotency_uq"
            )
        ]
        indexes = [models.Index(fields=["customer_email"]), models.Index(fields=["status"])]


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    creation = models.ForeignKey("creations.Creation", on_delete=models.PROTECT, related_name="+")
    version = models.ForeignKey(
        "creations.ImageVersion", on_delete=models.PROTECT, related_name="+"
    )
    model = models.ForeignKey("creations.Model3D", on_delete=models.PROTECT, related_name="+")
    size = models.ForeignKey("catalog.ProductSize", on_delete=models.PROTECT, related_name="+")
    size_label = models.CharField(max_length=40)
    longest_side_mm = models.PositiveIntegerField()
    quantity = models.PositiveSmallIntegerField()
    unit_price_cents = models.PositiveIntegerField()
    style = models.CharField(max_length=24)
    prompt_text = models.TextField(blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["created_at"]
