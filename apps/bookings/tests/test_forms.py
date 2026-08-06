from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.bookings.forms import BookingAdminUpdateForm, BookingCreateForm
from apps.bookings.models import Booking
from apps.resources.models import Resource


class BookingFormsTests(TestCase):
	def setUp(self) -> None:
		self.user = get_user_model().objects.create_user(
			username="alice",
			email="alice@example.com",
			password="test-password-123",
		)
		self.resource = Resource.objects.create(
			name="Workshop Room",
			capacity=10,
			opening_time=timezone.datetime(2026, 1, 1, 8, 0, tzinfo=timezone.get_current_timezone()).time(),
			closing_time=timezone.datetime(2026, 1, 1, 20, 0, tzinfo=timezone.get_current_timezone()).time(),
			max_booking_days_ahead=30,
			requires_approval=True,
		)
		starts_at = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
		self.booking = Booking.objects.create(
			resource=self.resource,
			user=self.user,
			title="Existing",
			starts_at=starts_at,
			ends_at=starts_at + timedelta(hours=1),
		)

	def test_create_form_makes_naive_datetimes_aware(self) -> None:
		form = BookingCreateForm(
			data={
				"resource": self.resource.id,
				"title": "Naive input",
				"notes": "",
				"starts_at": "2026-08-10T10:00",
				"ends_at": "2026-08-10T11:00",
			}
		)

		self.assertTrue(form.is_valid(), form.errors)
		self.assertFalse(timezone.is_naive(form.cleaned_data["starts_at"]))
		self.assertFalse(timezone.is_naive(form.cleaned_data["ends_at"]))

	def test_admin_update_form_makes_naive_datetimes_aware(self) -> None:
		form = BookingAdminUpdateForm(
			data={
				"title": "Updated",
				"notes": "Edited",
				"starts_at": "2026-08-10T12:00",
				"ends_at": "2026-08-10T13:00",
				"status": Booking.Status.CONFIRMED,
			},
			instance=self.booking,
		)

		self.assertTrue(form.is_valid(), form.errors)
		self.assertFalse(timezone.is_naive(form.cleaned_data["starts_at"]))
		self.assertFalse(timezone.is_naive(form.cleaned_data["ends_at"]))
