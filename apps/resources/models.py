from django.core.exceptions import ValidationError
from django.db import models


class Resource(models.Model):
	name = models.CharField(max_length=120, unique=True)
	description = models.TextField(blank=True)
	capacity = models.PositiveIntegerField(default=1)
	opening_time = models.TimeField()
	closing_time = models.TimeField()
	max_booking_days_ahead = models.PositiveIntegerField(default=90)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name"]
		constraints = [
			models.CheckConstraint(
				check=models.Q(capacity__gte=1),
				name="resource_capacity_gte_1",
			),
			models.CheckConstraint(
				check=models.Q(max_booking_days_ahead__gte=1),
				name="resource_max_booking_days_ahead_gte_1",
			),
		]

	def clean(self) -> None:
		super().clean()
		if self.opening_time >= self.closing_time:
			raise ValidationError("Opening time must be earlier than closing time.")

	def __str__(self) -> str:
		return self.name
