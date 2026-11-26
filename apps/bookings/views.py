from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.bookings.forms import BookingCreateForm
from apps.bookings.selectors import get_booking_by_id, get_user_bookings
from apps.bookings.services import BookingError, cancel_booking, create_booking


@login_required
def index(request: HttpRequest) -> HttpResponse:
	bookings = get_user_bookings(user=request.user)
	return render(request, "bookings/list.html", {"bookings": bookings})


@login_required
def create(request: HttpRequest) -> HttpResponse:
	if request.method == "POST":
		form = BookingCreateForm(request.POST)
		if form.is_valid():
			try:
				create_booking(
					resource=form.cleaned_data["resource"],
					user=request.user,
					title=form.cleaned_data["title"],
					notes=form.cleaned_data.get("notes", ""),
					starts_at=form.cleaned_data["starts_at"],
					ends_at=form.cleaned_data["ends_at"],
				)
				messages.success(request, "Booking created.")
				return redirect("bookings:index")
			except BookingError as exc:
				form.add_error(None, str(exc))
	else:
		form = BookingCreateForm()

	return render(request, "bookings/create.html", {"form": form})


@login_required
def cancel(request: HttpRequest, booking_id: int) -> HttpResponse:
	if request.method != "POST":
		return redirect("bookings:index")

	try:
		booking = get_booking_by_id(booking_id=booking_id)
	except ObjectDoesNotExist as exc:
		raise Http404 from exc

	try:
		cancel_booking(booking=booking, actor=request.user)
		messages.success(request, "Booking canceled.")
	except BookingError as exc:
		messages.error(request, str(exc))
	return redirect("bookings:index")
