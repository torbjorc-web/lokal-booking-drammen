from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.bookings.models import Booking
from apps.dashboard.selectors import get_dashboard_bookings
from apps.resources.models import Resource


class DashboardSelectorTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="test-password-123",
        )
        self.other_user = get_user_model().objects.create_user(
            username="bob",
            password="test-password-123",
        )

        self.resource = Resource.objects.create(
            name="Meeting Room A",
            capacity=8,
            opening_time=timezone.datetime(
                2026,
                1,
                1,
                8,
                0,
                tzinfo=timezone.get_current_timezone(),
            ).time(),
            closing_time=timezone.datetime(
                2026,
                1,
                1,
                20,
                0,
                tzinfo=timezone.get_current_timezone(),
            ).time(),
            max_booking_days_ahead=30,
            requires_approval=True,
        )

        self.other_resource = Resource.objects.create(
            name="Meeting Room B",
            capacity=12,
            opening_time=self.resource.opening_time,
            closing_time=self.resource.closing_time,
            max_booking_days_ahead=30,
            requires_approval=True,
        )

        base_start = (
            timezone.now()
            .replace(hour=10, minute=0, second=0, microsecond=0)
            + timedelta(days=1)
        )

        self.pending_booking = Booking.objects.create(
            resource=self.resource,
            user=self.user,
            title="Pending booking",
            starts_at=base_start,
            ends_at=base_start + timedelta(hours=1),
            status=Booking.Status.PENDING,
        )

        self.confirmed_booking = Booking.objects.create(
            resource=self.other_resource,
            user=self.other_user,
            title="Confirmed booking",
            starts_at=base_start + timedelta(hours=2),
            ends_at=base_start + timedelta(hours=3),
            status=Booking.Status.CONFIRMED,
        )

    def test_get_dashboard_bookings_orders_newest_first(self) -> None:
        bookings = list(get_dashboard_bookings())

        self.assertEqual(
            bookings,
            [self.confirmed_booking, self.pending_booking],
        )

    def test_get_dashboard_bookings_filters_by_status(self) -> None:
        bookings = list(
            get_dashboard_bookings(
                status=Booking.Status.PENDING,
            )
        )

        self.assertEqual(bookings, [self.pending_booking])

    def test_get_dashboard_bookings_filters_by_resource(self) -> None:
        bookings = list(
            get_dashboard_bookings(
                resource_id=str(self.resource.id),
            )
        )

        self.assertEqual(bookings, [self.pending_booking])

    def test_get_dashboard_bookings_filters_by_user(self) -> None:
        bookings = list(
            get_dashboard_bookings(
                user_id=str(self.other_user.id),
            )
        )

        self.assertEqual(bookings, [self.confirmed_booking])