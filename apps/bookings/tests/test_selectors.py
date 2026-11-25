from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.selectors import get_user_bookings
from apps.resources.models import Resource


class BookingSelectorTests(TestCase):
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
                                2026, 1, 1, 8, 0,
                                tzinfo=timezone.get_current_timezone(),
                        ).time(),
                        closing_time=timezone.datetime(
                                2026, 1, 1, 20, 0,
                                tzinfo=timezone.get_current_timezone(),
                        ).time(),
                        max_booking_days_ahead=30,
                        requires_approval=True,
                )

        def test_get_user_bookings_only_returns_users_bookings(self) -> None:
                starts_at = timezone.now() + timedelta(days=1)
                ends_at = starts_at + timedelta(hours=1)

                user_booking = Booking.objects.create(
                        resource=self.resource,
                        user=self.user,
                        title="Alice booking",
                        starts_at=starts_at,
                        ends_at=ends_at,
                )

                Booking.objects.create(
                        resource=self.resource,
                        user=self.other_user,
                        title="Bob booking",
                        starts_at=starts_at + timedelta(hours=2),
                        ends_at=ends_at + timedelta(hours=2),
                )

                bookings = get_user_bookings(user=self.user)

                self.assertEqual(list(bookings), [user_booking])

        def test_get_user_bookings_orders_newest_first(self) -> None:
                starts_at = timezone.now() + timedelta(days=1)

                older_booking = Booking.objects.create(
                        resource=self.resource,
                        user=self.user,
                        title="Older booking",
                        starts_at=starts_at,
                        ends_at=starts_at + timedelta(hours=1),
                )

                newer_booking = Booking.objects.create(
                        resource=self.resource,
                        user=self.user,
                        title="Newer booking",
                        starts_at=starts_at + timedelta(days=1),
                        ends_at=starts_at + timedelta(days=1, hours=1),
                )

                bookings = list(get_user_bookings(user=self.user))

                self.assertEqual(
                        bookings,
                        [newer_booking, older_booking],
                )