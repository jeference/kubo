from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/", include("accounts.urls")),
    path("api/", include("catalog.urls")),
    path("api/", include("media.urls")),
    path("api/", include("creations.urls")),
    path("api/", include("orders.urls")),
    path("api/", include("shipping.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("analytics.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    ]
