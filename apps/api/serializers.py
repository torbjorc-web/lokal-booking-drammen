from rest_framework import serializers

from apps.resources.models import Resource


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