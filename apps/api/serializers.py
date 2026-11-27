from rest_framework import serializers

from apps.bookings.models import Booking
from apps.resources.models import Resource


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "resource",
            "title",
            "notes",
            "starts_at",
            "ends_at",
            "status",
        ]


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
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
        ]