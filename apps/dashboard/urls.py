from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
	path("", views.index, name="index"),
	path("bookings/", views.booking_list, name="bookings"),
	path("bookings/export.csv", views.booking_export_csv, name="bookings_export_csv"),
	path("bookings/<int:booking_id>/status/", views.booking_set_status, name="bookings_set_status"),
	path("bookings/<int:booking_id>/edit/", views.booking_edit, name="bookings_edit"),
]
