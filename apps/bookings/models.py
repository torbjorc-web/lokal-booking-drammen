from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.resources.models import Resource


class Booking(models.Model):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		CONFIRMED = "confirmed", "Confirmed"
		CANCELED = "canceled", "Canceled"

	resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="bookings")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
	title = models.CharField(max_length=200)
	notes = models.TextField(blank=True)
	starts_at = models.DateTimeField()
	ends_at = models.DateTimeField()
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
	canceled_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["starts_at"]
		indexes = [
			models.Index(fields=["resource", "starts_at", "ends_at"], name="booking_resource_time_idx"),
			models.Index(fields=["user", "starts_at"], name="booking_user_time_idx"),
		]
		constraints = [
			models.CheckConstraint(
				check=models.Q(ends_at__gt=models.F("starts_at")),
				name="booking_ends_after_starts",
			),
		]

	def clean(self) -> None:
		super().clean()
		if self.starts_at >= self.ends_at:
			raise ValidationError("End time must be later than start time.")
		if timezone.is_naive(self.starts_at) or timezone.is_naive(self.ends_at):
			raise ValidationError("Booking times must be timezone-aware.")

	def __str__(self) -> str:
		return f"{self.resource} ({self.starts_at} - {self.ends_at})"
