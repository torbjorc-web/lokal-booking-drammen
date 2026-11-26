from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class BookingViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="test-password-123",
        )
        self.client.force_login(self.user)

    def test_cancel_nonexistent_booking_returns_404(self) -> None:
        response = self.client.post(
            reverse(
                "bookings:cancel",
                kwargs={"booking_id": 999999},
            )
        )

        self.assertEqual(response.status_code, 404)
