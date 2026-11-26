from django.db.models import QuerySet

from apps.bookings.models import Booking


def get_dashboard_bookings(
    *,
    status: str = "",
    resource_id: str = "",
    user_id: str = "",
) -> QuerySet[Booking]:
    queryset = (
        Booking.objects
        .select_related("resource", "user")
        .order_by("-starts_at")
    )

    if status:
        queryset = queryset.filter(status=status)

    if resource_id.isdigit():
        queryset = queryset.filter(resource_id=int(resource_id))

    if user_id.isdigit():
        queryset = queryset.filter(user_id=int(user_id))

    return queryset