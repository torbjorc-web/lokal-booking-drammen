from django.urls import path

from apps.api.views import (
    ApiRootView,
    BookingDetailView,
    BookingListView,
    ResourceListView,
)


app_name = "api"

urlpatterns = [
    path("", ApiRootView.as_view(), name="root"),
    path("resources/", ResourceListView.as_view(), name="resource-list"),
    path("bookings/", BookingListView.as_view(), name="booking-list"),
    path(
        "bookings/<int:pk>/",
        BookingDetailView.as_view(),
        name="booking-detail",
    ),
]
