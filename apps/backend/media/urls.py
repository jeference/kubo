from django.urls import path

from media.views import MediaView

urlpatterns = [path("media/<str:token>/", MediaView.as_view(), name="media")]
