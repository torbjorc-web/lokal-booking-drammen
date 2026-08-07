from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.bookings.models import Booking
from apps.resources.models import Resource


class DashboardViewsTests(TestCase):
	def setUp(self) -> None:
		self.staff_user = get_user_model().objects.create_user(
			username="admin",
			email="admin@example.com",
			password="test-password-123",
			is_staff=True,
		)
		self.member_user = get_user_model().objects.create_user(
			username="alice",
			email="alice@example.com",
			password="test-password-123",
		)
		self.resource = Resource.objects.create(
			name="Meeting Room B",
			capacity=12,
			opening_time=timezone.datetime(2026, 1, 1, 8, 0, tzinfo=timezone.get_current_timezone()).time(),
			closing_time=timezone.datetime(2026, 1, 1, 20, 0, tzinfo=timezone.get_current_timezone()).time(),
			max_booking_days_ahead=30,
			requires_approval=True,
		)

		base_start = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
		self.pending_booking = Booking.objects.create(
			resource=self.resource,
			user=self.member_user,
			title="Pending booking",
			starts_at=base_start,
			ends_at=base_start + timedelta(hours=1),
			status=Booking.Status.PENDING,
		)
		self.confirmed_booking = Booking.objects.create(
			resource=self.resource,
			user=self.member_user,
			title="Confirmed booking",
			starts_at=base_start + timedelta(hours=2),
			ends_at=base_start + timedelta(hours=3),
			status=Booking.Status.CONFIRMED,
		)

	def test_dashboard_index_requires_staff(self) -> None:
		self.client.login(username="alice", password="test-password-123")

		response = self.client.get(reverse("dashboard:index"))

		self.assertEqual(response.status_code, 302)
		self.assertIn("/admin/login/", response.url)

	def test_dashboard_index_renders_for_staff(self) -> None:
		self.client.login(username="admin", password="test-password-123")

		response = self.client.get(reverse("dashboard:index"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Dashboard")

	def test_booking_list_filters_by_status(self) -> None:
		self.client.login(username="admin", password="test-password-123")

		response = self.client.get(reverse("dashboard:bookings"), {"status": Booking.Status.PENDING})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Pending booking")
		self.assertNotContains(response, "Confirmed booking")

	def test_booking_set_status_changes_booking_for_staff(self) -> None:
		self.client.login(username="admin", password="test-password-123")

		response = self.client.post(
			reverse("dashboard:bookings_set_status", args=[self.pending_booking.id]),
			{"status": Booking.Status.CONFIRMED},
		)

		self.assertEqual(response.status_code, 302)
		self.pending_booking.refresh_from_db()
		self.assertEqual(self.pending_booking.status, Booking.Status.CONFIRMED)

	def test_booking_set_status_get_does_not_change_booking(self) -> None:
		self.client.login(username="admin", password="test-password-123")

		response = self.client.get(reverse("dashboard:bookings_set_status", args=[self.pending_booking.id]))

		self.assertEqual(response.status_code, 302)
		self.pending_booking.refresh_from_db()
		self.assertEqual(self.pending_booking.status, Booking.Status.PENDING)

	def test_booking_export_csv_returns_expected_content(self) -> None:
		self.client.login(username="admin", password="test-password-123")

		response = self.client.get(reverse("dashboard:bookings_export_csv"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response["Content-Type"], "text/csv")
		self.assertIn("attachment; filename=\"bookings.csv\"", response["Content-Disposition"])
		content = response.content.decode("utf-8")
		self.assertIn("ID,Resource,User,Title,Status,Starts,Ends,Created", content)
		self.assertIn("Pending booking", content)
