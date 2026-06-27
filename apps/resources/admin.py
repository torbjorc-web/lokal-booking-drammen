from django.contrib import admin

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
	list_display = ("name", "capacity", "opening_time", "closing_time", "is_active")
	search_fields = ("name",)
	list_filter = ("is_active",)
