from django.urls import path

from api.files.views import (
    MarathonFilesListView,
    MarathonFilesListViewNew,
)

urlpatterns = [
    # marathon all files list for participant
    path(
        "<int:marathon_id>/files/old/",
        MarathonFilesListView.as_view(),
        name="files-api-list-old",
    ),
    path(
        "<int:marathon_id>/files/",
        MarathonFilesListViewNew.as_view(),
        name="files-api-list",
    ),
]
