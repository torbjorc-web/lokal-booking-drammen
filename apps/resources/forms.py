from django import forms

from apps.resources.models import SavedSearch


class ResourceSearchForm(forms.Form):
	query = forms.CharField(label="Name contains", required=False, max_length=120)
	min_capacity = forms.IntegerField(label="Minimum capacity", required=False, min_value=1)
	search_date = forms.DateField(label="Date", required=False, widget=forms.DateInput(attrs={"type": "date"}))
	start_time = forms.TimeField(label="Start time", required=False, widget=forms.TimeInput(attrs={"type": "time"}))
	end_time = forms.TimeField(label="End time", required=False, widget=forms.TimeInput(attrs={"type": "time"}))

	def clean(self):
		cleaned_data = super().clean()
		start_time = cleaned_data.get("start_time")
		end_time = cleaned_data.get("end_time")
		if start_time and end_time and start_time >= end_time:
			raise forms.ValidationError("End time must be later than start time.")
		return cleaned_data


class SaveSearchForm(forms.ModelForm):
	class Meta:
		model = SavedSearch
		fields = ["name", "query", "min_capacity", "date", "start_time", "end_time"]
		widgets = {
			"date": forms.DateInput(attrs={"type": "date"}),
			"start_time": forms.TimeInput(attrs={"type": "time"}),
			"end_time": forms.TimeInput(attrs={"type": "time"}),
		}
