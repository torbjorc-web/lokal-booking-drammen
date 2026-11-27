from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from apps.bookings.models import Booking
from apps.resources.models import Resource


class BookingDetailApiTests(APITestCase):
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
            description="Room for meetings",
            capacity=8,
            opening_time=time(8, 0),
            closing_time=time(20, 0),
        )

        starts_at = timezone.now() + timedelta(days=1)

        self.booking = Booking.objects.create(
            resource=self.resource,
            user=self.user,
            title="Alice booking",
            notes="My booking",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=1),
            status=Booking.Status.CONFIRMED,
        )

        self.other_booking = Booking.objects.create(
            resource=self.resource,
            user=self.other_user,
            title="Bob booking",
            notes="Another user's booking",
            starts_at=starts_at + timedelta(hours=2),
            ends_at=starts_at + timedelta(hours=3),
            status=Booking.Status.CONFIRMED,
        )

    def test_booking_detail_requires_authentication(self) -> None:
        response = self.client.get(
            reverse(
                "api:booking-detail",
                kwargs={"pk": self.booking.pk},
            )
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_booking_detail_returns_current_users_booking(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                "api:booking-detail",
                kwargs={"pk": self.booking.pk},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.booking.id)
        self.assertEqual(response.data["title"], "Alice booking")

    def test_booking_detail_does_not_return_other_users_booking(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                "api:booking-detail",
                kwargs={"pk": self.other_booking.pk},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_booking_detail_returns_expected_fields(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse(
                "api:booking-detail",
                kwargs={"pk": self.booking.pk},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "resource",
                "title",
                "notes",
                "starts_at",
                "ends_at",
                "status",
            },
        )
