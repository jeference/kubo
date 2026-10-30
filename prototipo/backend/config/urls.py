"""Root URL configuration. App routes live under /api/ ; each app owns its urls.py."""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

api_patterns = [
    path("", include("generation.urls")),
]

urlpatterns = [
    path("api/", include(api_patterns)),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
