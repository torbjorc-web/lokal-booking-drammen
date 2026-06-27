from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.services import (
	BookingConflictError,
	BookingValidationError,
	create_booking,
)
from apps.resources.models import Resource


class CreateBookingServiceTests(TestCase):
	def setUp(self) -> None:
		self.user = get_user_model().objects.create_user(
			username="alice",
			email="alice@example.com",
			password="test-password-123",
		)
		self.resource = Resource.objects.create(
			name="Meeting Room A",
			capacity=8,
			opening_time=timezone.datetime(2026, 1, 1, 8, 0, tzinfo=timezone.get_current_timezone()).time(),
			closing_time=timezone.datetime(2026, 1, 1, 20, 0, tzinfo=timezone.get_current_timezone()).time(),
			max_booking_days_ahead=30,
		)

	def test_create_booking_success(self) -> None:
		starts_at = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
		ends_at = starts_at + timedelta(hours=2)

		booking = create_booking(
			resource=self.resource,
			user=self.user,
			title="Team Standup",
			starts_at=starts_at,
			ends_at=ends_at,
		)

		self.assertEqual(booking.status, Booking.Status.CONFIRMED)
		self.assertEqual(Booking.objects.count(), 1)

	def test_create_booking_conflict_raises(self) -> None:
		starts_at = timezone.now().replace(hour=11, minute=0, second=0, microsecond=0) + timedelta(days=1)
		ends_at = starts_at + timedelta(hours=2)

		Booking.objects.create(
			resource=self.resource,
			user=self.user,
			title="Existing",
			starts_at=starts_at,
			ends_at=ends_at,
			status=Booking.Status.CONFIRMED,
		)

		with self.assertRaises(BookingConflictError):
			create_booking(
				resource=self.resource,
				user=self.user,
				title="Overlap",
				starts_at=starts_at + timedelta(minutes=30),
				ends_at=ends_at + timedelta(minutes=30),
			)

	def test_create_booking_outside_opening_hours_raises(self) -> None:
		starts_at = timezone.now().replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=1)
		ends_at = starts_at + timedelta(hours=2)

		with self.assertRaises(BookingValidationError):
			create_booking(
				resource=self.resource,
				user=self.user,
				title="Too Early",
				starts_at=starts_at,
				ends_at=ends_at,
			)

	def test_create_booking_too_far_ahead_raises(self) -> None:
		starts_at = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=45)
		ends_at = starts_at + timedelta(hours=1)

		with self.assertRaises(BookingValidationError):
			create_booking(
				resource=self.resource,
				user=self.user,
				title="Too Far Ahead",
				starts_at=starts_at,
				ends_at=ends_at,
			)
