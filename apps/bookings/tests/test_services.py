from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.core import mail
from django.test import override_settings

from apps.bookings.models import Booking
from apps.bookings.services import (
	BookingConflictError,
	BookingPermissionError,
	BookingValidationError,
	cancel_booking,
	create_booking,
	set_booking_status,
)
from apps.resources.models import Resource


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class CreateBookingServiceTests(TestCase):
	def setUp(self) -> None:
		self.user = get_user_model().objects.create_user(
			username="alice",
			email="alice@example.com",
			password="test-password-123",
		)
		self.staff_user = get_user_model().objects.create_user(
			username="admin",
			email="admin@example.com",
			password="test-password-123",
			is_staff=True,
		)
		self.resource = Resource.objects.create(
			name="Meeting Room A",
			capacity=8,
			opening_time=timezone.datetime(2026, 1, 1, 8, 0, tzinfo=timezone.get_current_timezone()).time(),
			closing_time=timezone.datetime(2026, 1, 1, 20, 0, tzinfo=timezone.get_current_timezone()).time(),
			max_booking_days_ahead=30,
			requires_approval=True,
		)

	def test_create_booking_success(self) -> None:
		starts_at = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
		ends_at = starts_at + timedelta(hours=2)

		with self.captureOnCommitCallbacks(execute=True):
			booking = create_booking(
				resource=self.resource,
				user=self.user,
				title="Team Standup",
				starts_at=starts_at,
				ends_at=ends_at,
			)

		self.assertEqual(booking.status, Booking.Status.PENDING)
		self.assertEqual(Booking.objects.count(), 1)
		self.assertEqual(len(mail.outbox), 1)

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

	def test_cancel_booking_deadline_raises_for_member(self) -> None:
		starts_at = timezone.now() + timedelta(hours=2)
		ends_at = starts_at + timedelta(hours=1)
		booking = Booking.objects.create(
			resource=self.resource,
			user=self.user,
			title="Late cancel",
			starts_at=starts_at,
			ends_at=ends_at,
			status=Booking.Status.PENDING,
		)

		with self.assertRaises(BookingValidationError):
			cancel_booking(booking=booking, actor=self.user)

	def test_user_cannot_cancel_another_users_booking(self) -> None:
		other_user = get_user_model().objects.create_user(
			username="bob",
			password="test-password-123",
		)

		starts_at = timezone.now() + timedelta(days=1)
		ends_at = starts_at + timedelta(hours=1)

		booking = Booking.objects.create(
			resource=self.resource,
			user=self.user,
			title="Alice booking",
			starts_at=starts_at,
			ends_at=ends_at,
			status=Booking.Status.PENDING,
		)

		with self.assertRaises(BookingPermissionError):
			cancel_booking(
				booking=booking,
				actor=other_user,
			)

		booking.refresh_from_db()

		self.assertEqual(booking.status, Booking.Status.PENDING)
		self.assertIsNone(booking.canceled_at)

	def test_cancel_booking_allowed_for_staff_override(self) -> None:
		starts_at = timezone.now() + timedelta(hours=2)
		ends_at = starts_at + timedelta(hours=1)
		booking = Booking.objects.create(
			resource=self.resource,
			user=self.user,
			title="Staff override",
			starts_at=starts_at,
			ends_at=ends_at,
			status=Booking.Status.PENDING,
		)

		cancel_booking(booking=booking, actor=self.staff_user)
		booking.refresh_from_db()
		self.assertEqual(booking.status, Booking.Status.CANCELED)

	def test_only_staff_can_change_status(self) -> None:
		starts_at = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=2)
		ends_at = starts_at + timedelta(hours=1)
		with self.captureOnCommitCallbacks(execute=True):
			booking = create_booking(
				resource=self.resource,
				user=self.user,
				title="Approval",
				starts_at=starts_at,
				ends_at=ends_at,
			)

		with self.assertRaises(BookingPermissionError):
			set_booking_status(booking=booking, status=Booking.Status.CONFIRMED, actor=self.user)

		with self.captureOnCommitCallbacks(execute=True):
			set_booking_status(booking=booking, status=Booking.Status.CONFIRMED, actor=self.staff_user)
		booking.refresh_from_db()
		self.assertEqual(booking.status, Booking.Status.CONFIRMED)
		self.assertGreaterEqual(len(mail.outbox), 2)

	def test_canceled_booking_cannot_be_reopened(self) -> None:
		starts_at = (
			timezone.now().replace(
				hour=10,
				minute=0,
				second=0,
				microsecond=0,
			)
			+ timedelta(days=2)
		)
		ends_at = starts_at + timedelta(hours=1)

		booking = Booking.objects.create(
			resource=self.resource,
			user=self.user,
			title="Canceled booking",
			starts_at=starts_at,
			ends_at=ends_at,
			status=Booking.Status.CANCELED,
			canceled_at=timezone.now(),
		)

		with self.assertRaises(BookingValidationError):
			set_booking_status(
				booking=booking,
				status=Booking.Status.CONFIRMED,
				actor=self.staff_user,
			)

	def test_booking_created_email_is_deferred_until_commit(self) -> None:
		starts_at = (
			timezone.now().replace(
				hour=10,
				minute=0,
				second=0,
				microsecond=0,
			)
			+ timedelta(days=1)
		)
		ends_at = starts_at + timedelta(hours=1)

		with self.captureOnCommitCallbacks(execute=False) as callbacks:
			create_booking(
				resource=self.resource,
				user=self.user,
				title="Deferred notification",
				starts_at=starts_at,
				ends_at=ends_at,
			)

			self.assertEqual(len(mail.outbox), 0)

		self.assertEqual(len(callbacks), 1)

		callbacks[0]()

		self.assertEqual(len(mail.outbox), 1)

	def test_cancel_booking_email_is_deferred_until_commit(self) -> None:
		starts_at = timezone.now() + timedelta(days=2)
		ends_at = starts_at + timedelta(hours=1)

		booking = Booking.objects.create(
			resource=self.resource,
			user=self.user,
			title="Deferred cancellation notification",
			starts_at=starts_at,
			ends_at=ends_at,
			status=Booking.Status.PENDING,
		)

		with self.captureOnCommitCallbacks(execute=False) as callbacks:
			cancel_booking(
				booking=booking,
				actor=self.user,
			)

			self.assertEqual(len(mail.outbox), 0)

		self.assertEqual(len(callbacks), 1)

		callbacks[0]()

		self.assertEqual(len(mail.outbox), 1)

	def test_status_changed_email_is_deferred_until_commit(self) -> None:
		starts_at = timezone.now() + timedelta(days=2)
		ends_at = starts_at + timedelta(hours=1)

		booking = Booking.objects.create(
			resource=self.resource,
			user=self.user,
			title="Deferred status notification",
			starts_at=starts_at,
			ends_at=ends_at,
			status=Booking.Status.PENDING,
		)

		with self.captureOnCommitCallbacks(execute=False) as callbacks:
			set_booking_status(
				booking=booking,
				status=Booking.Status.CONFIRMED,
				actor=self.staff_user,
			)

			self.assertEqual(len(mail.outbox), 0)

		self.assertEqual(len(callbacks), 1)

		callbacks[0]()

		self.assertEqual(len(mail.outbox), 1)
