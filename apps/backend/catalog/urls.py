from django.urls import path

from catalog import views

urlpatterns = [
    path("catalog/styles/", views.StyleListView.as_view(), name="catalog-styles"),
    path("catalog/sizes/", views.SizeListView.as_view(), name="catalog-sizes"),
]
