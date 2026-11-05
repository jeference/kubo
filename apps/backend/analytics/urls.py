from django.urls import path

from analytics.views import EventView

urlpatterns = [path("events/", EventView.as_view(), name="events")]
