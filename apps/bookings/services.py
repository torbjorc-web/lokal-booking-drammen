from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from apps.bookings.models import Booking
from apps.notifications.services import (
	send_booking_created_email,
	send_booking_status_changed_email,
)
from apps.resources.models import Resource


class BookingError(Exception):
	pass


class BookingValidationError(BookingError):
	pass


class BookingConflictError(BookingError):
	pass


class BookingPermissionError(BookingError):
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

	duration_minutes = int((ends_at - starts_at).total_seconds() / 60)
	if duration_minutes > resource.max_booking_duration_minutes:
		raise BookingValidationError("Booking exceeds resource maximum duration.")


@transaction.atomic
def create_booking(
	*,
	resource: Resource,
	user,
	title: str,
	starts_at: datetime,
	ends_at: datetime,
	notes: str = "",
	status: str | None = None,
) -> Booking:
	if starts_at >= ends_at:
		raise BookingValidationError("End time must be later than start time.")

	if timezone.is_naive(starts_at) or timezone.is_naive(ends_at):
		raise BookingValidationError("Booking times must be timezone-aware.")

	resource = Resource.objects.select_for_update().get(pk=resource.pk)
	_validate_resource_window(resource, starts_at, ends_at)

	if has_conflict(resource=resource, starts_at=starts_at, ends_at=ends_at):
		raise BookingConflictError("Resource is already booked for this time range.")

	if status is None:
		status = Booking.Status.PENDING if resource.requires_approval else Booking.Status.CONFIRMED

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
	send_booking_created_email(booking)
	return booking


@transaction.atomic
def cancel_booking(*, booking: Booking, actor) -> Booking:
	if actor != booking.user and not actor.is_staff:
		raise BookingPermissionError("You do not have permission to cancel this booking.")

	if booking.status == Booking.Status.CANCELED:
		return booking

	deadline = booking.starts_at - timedelta(hours=booking.resource.cancellation_deadline_hours)
	if timezone.now() > deadline and not actor.is_staff:
		raise BookingValidationError("Cancellation deadline has passed for this booking.")

	booking.status = Booking.Status.CANCELED
	booking.canceled_at = timezone.now()
	booking.save(update_fields=["status", "canceled_at", "updated_at"])
	send_booking_status_changed_email(booking)
	return booking


@transaction.atomic
def set_booking_status(*, booking: Booking, status: str, actor) -> Booking:
	if not actor.is_staff:
		raise BookingPermissionError("Only administrators can change booking status.")

	if status not in dict(Booking.Status.choices):
		raise BookingValidationError("Invalid booking status.")

	booking.status = status
	if status == Booking.Status.CANCELED and booking.canceled_at is None:
		booking.canceled_at = timezone.now()
	elif status != Booking.Status.CANCELED:
		booking.canceled_at = None
	booking.full_clean()
	booking.save()
	send_booking_status_changed_email(booking)
	return booking
