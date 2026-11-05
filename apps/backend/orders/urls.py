from django.urls import path

from orders import views

urlpatterns = [
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/items/", views.CartItemListView.as_view(), name="cart-items"),
    path("cart/items/<uuid:item_id>/", views.CartItemDetailView.as_view(), name="cart-item"),
    path("orders/", views.OrderListView.as_view(), name="orders"),
    path(
        "orders/track/resend/", views.OrderTrackingResendView.as_view(), name="order-track-resend"
    ),
    path("orders/track/<str:token>/", views.OrderTrackingView.as_view(), name="order-track"),
    path("orders/<uuid:order_id>/", views.OrderDetailView.as_view(), name="order"),
    path("orders/<uuid:order_id>/pay/", views.OrderPayView.as_view(), name="order-pay"),
    path("me/addresses/", views.AddressListView.as_view(), name="me-addresses"),
]
