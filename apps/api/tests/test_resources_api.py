from datetime import time

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.resources.models import Resource


class ResourceApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="test-password-123",
        )

        self.active_resource = Resource.objects.create(
            name="Meeting Room A",
            description="Room for meetings",
            capacity=8,
            opening_time=time(8, 0),
            closing_time=time(20, 0),
            max_booking_days_ahead=30,
            max_booking_duration_minutes=120,
            cancellation_deadline_hours=24,
            requires_approval=True,
            is_active=True,
        )

        self.inactive_resource = Resource.objects.create(
            name="Meeting Room B",
            description="Inactive room",
            capacity=12,
            opening_time=time(8, 0),
            closing_time=time(20, 0),
            max_booking_days_ahead=30,
            max_booking_duration_minutes=180,
            cancellation_deadline_hours=24,
            requires_approval=False,
            is_active=False,
        )

    def test_resource_list_requires_authentication(self) -> None:
        response = self.client.get(reverse("api:resource-list"))

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_resource_list_returns_active_resources(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("api:resource-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.active_resource.id)
        self.assertEqual(response.data[0]["name"], "Meeting Room A")

    def test_resource_list_does_not_return_inactive_resources(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("api:resource-list"))

        resource_ids = [resource["id"] for resource in response.data]

        self.assertIn(self.active_resource.id, resource_ids)
        self.assertNotIn(self.inactive_resource.id, resource_ids)

    def test_resource_list_returns_expected_fields(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("api:resource-list"))

        self.assertEqual(
            set(response.data[0].keys()),
            {
                "id",
                "name",
                "description",
                "capacity",
                "opening_time",
                "closing_time",
                "max_booking_days_ahead",
                "max_booking_duration_minutes",
                "cancellation_deadline_hours",
                "requires_approval",
            },
        )