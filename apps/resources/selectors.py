from datetime import date, time

from django.db.models import QuerySet

from apps.resources.models import Resource


def search_resources(
	*,
	query: str = "",
	min_capacity: int | None = None,
	search_date: date | None = None,
	start_time: time | None = None,
	end_time: time | None = None,
) -> QuerySet[Resource]:
	resources = Resource.objects.filter(is_active=True)

	if query:
		resources = resources.filter(name__icontains=query)
	if min_capacity:
		resources = resources.filter(capacity__gte=min_capacity)

	if search_date and start_time and end_time:
		# Avoid an app-level import cycle: bookings.services imports resources.models.
		from apps.bookings.services import has_conflict
		from django.utils import timezone

		starts_at = timezone.make_aware(timezone.datetime.combine(search_date, start_time))
		ends_at = timezone.make_aware(timezone.datetime.combine(search_date, end_time))
		resources = [
			resource
			for resource in resources
			if resource.opening_time <= start_time
			and end_time <= resource.closing_time
			and not has_conflict(resource=resource, starts_at=starts_at, ends_at=ends_at)
		]

	return resources
