from django.urls import path

from payments.views import AbacatePayWebhookView

urlpatterns = [
    path("webhooks/abacatepay/", AbacatePayWebhookView.as_view(), name="webhook-abacatepay"),
]
