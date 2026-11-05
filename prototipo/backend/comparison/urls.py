from django.urls import path

from comparison import views

urlpatterns = [
    path("comparison/models/", views.CatalogView.as_view(), name="comparison-models"),
    path("comparison/runs/", views.RunsView.as_view(), name="comparison-runs"),
    path("comparison/runs/<uuid:id>/", views.RunDetailView.as_view(), name="comparison-run"),
]
