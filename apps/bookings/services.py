from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from apps.bookings.models import Booking
from apps.resources.models import Resource


class BookingError(Exception):
	pass


class BookingValidationError(BookingError):
	pass


class BookingConflictError(BookingError):
	pass


def has_conflict(resource: Resource, starts_at: datetime, ends_at: datetime, exclude_booking_id: int | None = None) -> bool:
	queryset = Booking.objects.filter(
		resource=resource,
		status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
		starts_at__lt=ends_at,
		ends_at__gt=starts_at,
	)
	if exclude_booking_id is not None:
		queryset = queryset.exclude(id=exclude_booking_id)
	return queryset.exists()


def _validate_resource_window(resource: Resource, starts_at: datetime, ends_at: datetime) -> None:
	if not resource.is_active:
		raise BookingValidationError("Resource is not active.")

	now = timezone.now()
	latest_allowed_start = now + timedelta(days=resource.max_booking_days_ahead)
	if starts_at > latest_allowed_start:
		raise BookingValidationError("Booking starts too far ahead in time.")

	if starts_at.time() < resource.opening_time or ends_at.time() > resource.closing_time:
		raise BookingValidationError("Booking must be within resource opening hours.")


@transaction.atomic
def create_booking(
	*,
	resource: Resource,
	user,
	title: str,
	starts_at: datetime,
	ends_at: datetime,
	notes: str = "",
	status: str = Booking.Status.CONFIRMED,
) -> Booking:
	if starts_at >= ends_at:
		raise BookingValidationError("End time must be later than start time.")

	if timezone.is_naive(starts_at) or timezone.is_naive(ends_at):
		raise BookingValidationError("Booking times must be timezone-aware.")

	resource = Resource.objects.select_for_update().get(pk=resource.pk)
	_validate_resource_window(resource, starts_at, ends_at)

	if has_conflict(resource=resource, starts_at=starts_at, ends_at=ends_at):
		raise BookingConflictError("Resource is already booked for this time range.")

	booking = Booking(
		resource=resource,
		user=user,
		title=title,
		notes=notes,
		starts_at=starts_at,
		ends_at=ends_at,
		status=status,
	)
	booking.full_clean()
	booking.save()
	return booking
