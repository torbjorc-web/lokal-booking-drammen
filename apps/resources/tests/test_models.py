from datetime import time

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.resources.models import Resource


class ResourceModelTests(TestCase):
	def test_opening_time_must_be_before_closing_time(self) -> None:
		resource = Resource(
			name="Gym Hall",
			capacity=20,
			opening_time=time(20, 0),
			closing_time=time(8, 0),
		)

		with self.assertRaises(ValidationError):
			resource.full_clean()

	def test_valid_resource_times_pass_validation(self) -> None:
		resource = Resource(
			name="Classroom A",
			capacity=16,
			opening_time=time(8, 0),
			closing_time=time(20, 0),
		)

		resource.full_clean()
