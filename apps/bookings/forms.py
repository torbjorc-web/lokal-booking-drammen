from django import forms
from django.utils import timezone

from apps.bookings.models import Booking


class BookingCreateForm(forms.ModelForm):
	class Meta:
		model = Booking
		fields = ["resource", "title", "notes", "starts_at", "ends_at"]
		widgets = {
			"starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
			"ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
		}

	def clean(self):
		cleaned_data = super().clean()
		for field_name in ["starts_at", "ends_at"]:
			value = cleaned_data.get(field_name)
			if value is not None and timezone.is_naive(value):
				cleaned_data[field_name] = timezone.make_aware(value, timezone.get_current_timezone())
		return cleaned_data


class BookingAdminUpdateForm(forms.ModelForm):
	class Meta:
		model = Booking
		fields = ["title", "notes", "starts_at", "ends_at", "status"]
		widgets = {
			"starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
			"ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
		}

	def clean(self):
		cleaned_data = super().clean()
		for field_name in ["starts_at", "ends_at"]:
			value = cleaned_data.get(field_name)
			if value is not None and timezone.is_naive(value):
				cleaned_data[field_name] = timezone.make_aware(value, timezone.get_current_timezone())
		return cleaned_data
