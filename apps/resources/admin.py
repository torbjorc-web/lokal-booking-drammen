from django.contrib import admin

from .models import Resource, SavedSearch


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
	list_display = ("name", "capacity", "opening_time", "closing_time", "is_active")
	search_fields = ("name",)
	list_filter = ("is_active",)


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
	list_display = ("name", "user", "query", "min_capacity", "date", "created_at")
	search_fields = ("name", "query", "user__username")
	list_filter = ("date",)
