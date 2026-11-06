from django.urls import path

from creations import views

urlpatterns = [
    path("quota/", views.QuotaView.as_view(), name="quota"),
    path("creations/", views.CreationListView.as_view(), name="creation-list"),
    path("creations/<uuid:creation_id>/", views.CreationDetailView.as_view(), name="creation"),
    path(
        "creations/<uuid:creation_id>/retry/",
        views.CreationRetryView.as_view(),
        name="creation-retry",
    ),
    path(
        "creations/<uuid:creation_id>/edits/",
        views.CreationEditView.as_view(),
        name="creation-edits",
    ),
    path(
        "creations/<uuid:creation_id>/edits/<uuid:task_id>/cancel/",
        views.CreationEditCancelView.as_view(),
        name="creation-edit-cancel",
    ),
    path(
        "creations/<uuid:creation_id>/apply-version/",
        views.CreationApplyVersionView.as_view(),
        name="creation-apply-version",
    ),
]
