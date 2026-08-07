from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView


def healthz(request):
	# Lightweight endpoint for uptime pings; avoids DB access to keep it fast/cheap.
	return HttpResponse("ok")


urlpatterns = [
	path("admin/", admin.site.urls),
	path("healthz/", healthz, name="healthz"),
	path("", TemplateView.as_view(template_name="home.html"), name="home"),
	path("auth/", include("django.contrib.auth.urls")),
	path("accounts/", include("apps.accounts.urls")),
	path("resources/", include("apps.resources.urls")),
	path("bookings/", include("apps.bookings.urls")),
	path("dashboard/", include("apps.dashboard.urls")),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
