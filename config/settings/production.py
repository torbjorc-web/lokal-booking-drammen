from .base import *  # noqa: F403,F401
import os

import dj_database_url

DEBUG = False

MIDDLEWARE = ["whitenoise.middleware.WhiteNoiseMiddleware", *MIDDLEWARE]  # noqa: F405

STORAGES = {
	"default": {
		"BACKEND": "django.core.files.storage.FileSystemStorage",
	},
	"staticfiles": {
		"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
	},
}

DATABASES = {
	"default": dj_database_url.config(
		default=os.getenv("DATABASE_URL"),
		conn_max_age=600,
		ssl_require=True,
	)
}

render_external_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_external_hostname:
	ALLOWED_HOSTS.append(render_external_hostname)  # noqa: F405
	CSRF_TRUSTED_ORIGINS.append(f"https://{render_external_hostname}")  # noqa: F405

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
