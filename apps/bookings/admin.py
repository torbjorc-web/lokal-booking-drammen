from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ("resource", "user", "starts_at", "ends_at", "status")
	search_fields = ("title", "resource__name", "user__username")
	list_filter = ("status", "resource")
