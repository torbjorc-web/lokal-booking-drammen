from django.urls import path

app_name = "accounts"

urlpatterns = [
	path("", lambda request: None, name="index"),
]
