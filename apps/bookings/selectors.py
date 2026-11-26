from django.db.models import QuerySet

from apps.bookings.models import Booking


def get_booking_by_id(
    *,
    booking_id: int,
) -> Booking:
    return (
        Booking.objects
        .select_related("resource", "user")
        .get(pk=booking_id)
    )


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
