from django.urls import path

from generation import views

urlpatterns = [
    path("generation/images/", views.GenerateImagesView.as_view(), name="generate-images"),
    path("generation/images/upload/", views.UploadImageView.as_view(), name="upload-image"),
    path("generation/images/<uuid:id>/edit/", views.EditImageView.as_view(), name="edit-image"),
    path("generation/models/", views.ModelsView.as_view(), name="models"),
    path("generation/models/<uuid:id>/", views.ModelDetailView.as_view(), name="model-detail"),
    path("generation/credits/", views.CreditsView.as_view(), name="credits"),
]
