from django.urls import path

from generation import views

urlpatterns = [
    path("generation/images/", views.GenerateImagesView.as_view(), name="generate-images"),
    path("generation/images/upload/", views.UploadImageView.as_view(), name="upload-image"),
    path("generation/models/", views.ModelsView.as_view(), name="models"),
    path("generation/models/<uuid:id>/", views.ModelDetailView.as_view(), name="model-detail"),
]
