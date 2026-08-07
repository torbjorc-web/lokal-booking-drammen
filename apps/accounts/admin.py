from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.http import HttpRequest

from .models import User


def _has_permission(self: AdminSite, request: HttpRequest) -> bool:
	# Only superusers may access the admin site, regardless of is_staff.
	return request.user.is_active and request.user.is_superuser


AdminSite.has_permission = _has_permission


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (("Profile", {"fields": ("phone_number",)}),)
