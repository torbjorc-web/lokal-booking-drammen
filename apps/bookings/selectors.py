from django.db.models import QuerySet

from apps.bookings.models import Booking


def get_user_bookings(
    *,
    user,
) -> QuerySet[Booking]:
    return (
        Booking.objects
        .filter(user=user)
        .select_related("resource")
        .order_by("-starts_at")
    )
