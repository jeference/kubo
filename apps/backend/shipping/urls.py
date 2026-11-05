from django.urls import path

from shipping import views

urlpatterns = [
    path("shipping/quotes/", views.ShippingQuoteView.as_view(), name="shipping-quotes"),
    path(
        "shipping/address/<str:postal_code>/",
        views.AddressLookupView.as_view(),
        name="shipping-address",
    ),
]
