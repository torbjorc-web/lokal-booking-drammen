from django.conf import settings
from django.core.mail import send_mail


def _send_booking_email(*, recipient: str, subject: str, body: str) -> None:
	if not recipient:
		return
	send_mail(
		subject=subject,
		message=body,
		from_email=settings.DEFAULT_FROM_EMAIL,
		recipient_list=[recipient],
		fail_silently=True,
	)


def send_booking_created_email(booking) -> None:
	resource_name = booking.resource.name
	_send_booking_email(
		recipient=booking.user.email,
		subject=f"Booking received: {resource_name}",
		body=(
			f"Hi {booking.user.get_username()},\n\n"
			f"Your booking request for {resource_name} is registered with status '{booking.status}'.\n"
			f"Starts: {booking.starts_at}\n"
			f"Ends: {booking.ends_at}\n\n"
			"You can view your bookings in the app."
		),
	)


def send_booking_status_changed_email(booking) -> None:
	resource_name = booking.resource.name
	_send_booking_email(
		recipient=booking.user.email,
		subject=f"Booking update: {resource_name}",
		body=(
			f"Hi {booking.user.get_username()},\n\n"
			f"The booking status is now '{booking.status}'.\n"
			f"Starts: {booking.starts_at}\n"
			f"Ends: {booking.ends_at}\n"
		),
	)
