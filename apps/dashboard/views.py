import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.bookings.forms import BookingAdminUpdateForm
from apps.bookings.models import Booking
from apps.bookings.services import BookingError, set_booking_status


@staff_member_required
def index(request: HttpRequest) -> HttpResponse:
	metrics = {
		"total": Booking.objects.count(),
		"pending": Booking.objects.filter(status=Booking.Status.PENDING).count(),
		"confirmed": Booking.objects.filter(status=Booking.Status.CONFIRMED).count(),
		"canceled": Booking.objects.filter(status=Booking.Status.CANCELED).count(),
		"by_resource": Booking.objects.values("resource__name").annotate(total=Count("id")).order_by("resource__name"),
	}
	return render(request, "dashboard/index.html", {"metrics": metrics})


@staff_member_required
def booking_list(request: HttpRequest) -> HttpResponse:
	queryset = Booking.objects.select_related("resource", "user").order_by("-starts_at")

	status = request.GET.get("status", "").strip()
	resource_id = request.GET.get("resource", "").strip()
	user_id = request.GET.get("user", "").strip()

	if status:
		queryset = queryset.filter(status=status)
	if resource_id.isdigit():
		queryset = queryset.filter(resource_id=int(resource_id))
	if user_id.isdigit():
		queryset = queryset.filter(user_id=int(user_id))

	context = {
		"bookings": queryset,
		"filters": {
			"status": status,
			"resource": resource_id,
			"user": user_id,
		},
		"status_choices": Booking.Status.choices,
	}
	return render(request, "dashboard/bookings_list.html", context)


@staff_member_required
def booking_set_status(request: HttpRequest, booking_id: int) -> HttpResponse:
	if request.method != "POST":
		return redirect("dashboard:bookings")

	booking = get_object_or_404(Booking.objects.select_related("resource", "user"), pk=booking_id)
	status = request.POST.get("status", "")
	try:
		set_booking_status(booking=booking, status=status, actor=request.user)
		messages.success(request, "Booking status updated.")
	except BookingError as exc:
		messages.error(request, str(exc))
	return redirect("dashboard:bookings")


@staff_member_required
def booking_edit(request: HttpRequest, booking_id: int) -> HttpResponse:
	booking = get_object_or_404(Booking.objects.select_related("resource", "user"), pk=booking_id)

	if request.method == "POST":
		form = BookingAdminUpdateForm(request.POST, instance=booking)
		if form.is_valid():
			form.save()
			messages.success(request, "Booking updated.")
			return redirect("dashboard:bookings")
	else:
		form = BookingAdminUpdateForm(instance=booking)

	return render(request, "dashboard/booking_edit.html", {"form": form, "booking": booking})


@staff_member_required
def booking_export_csv(request: HttpRequest) -> HttpResponse:
	queryset = Booking.objects.select_related("resource", "user").order_by("starts_at")

	response = HttpResponse(content_type="text/csv")
	response["Content-Disposition"] = 'attachment; filename="bookings.csv"'

	writer = csv.writer(response)
	writer.writerow(["ID", "Resource", "User", "Title", "Status", "Starts", "Ends", "Created"])
	for booking in queryset:
		writer.writerow(
			[
				booking.id,
				booking.resource.name,
				booking.user.get_username(),
				booking.title,
				booking.status,
				booking.starts_at,
				booking.ends_at,
				booking.created_at,
			]
		)

	return response
