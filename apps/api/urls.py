from django.urls import path

from apps.api.views import ApiRootView, ResourceListView


app_name = "api"

urlpatterns = [
    path("", ApiRootView.as_view(), name="root"),
    path("resources/", ResourceListView.as_view(), name="resource-list"),
]
