from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ApiRootTests(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="alice",
            password="test-password-123",
        )

    def test_api_root_requires_authentication(self) -> None:
        response = self.client.get(reverse("api:root"))

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ],
        )

    def test_api_root_returns_v1_for_authenticated_user(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("api:root"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["version"], "v1")