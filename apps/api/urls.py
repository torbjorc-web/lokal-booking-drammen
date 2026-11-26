from django.urls import path

from apps.api.views import ApiRootView


app_name = "api"

urlpatterns = [
    path("", ApiRootView.as_view(), name="root"),
]