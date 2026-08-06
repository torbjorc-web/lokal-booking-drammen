#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input

if [ -z "${DATABASE_URL:-}" ]; then
	echo "ERROR: DATABASE_URL is not set."
	echo "Set DATABASE_URL from your Render PostgreSQL service connection string."
	exit 1
fi

attempt=1
max_attempts=5
until python manage.py migrate; do
	if [ "$attempt" -ge "$max_attempts" ]; then
		echo "ERROR: Migrations failed after ${max_attempts} attempts."
		echo "If hostname resolution failed, verify DATABASE_URL points to an existing Render database."
		exit 1
	fi

	echo "Migration attempt ${attempt} failed. Retrying in 5 seconds..."
	attempt=$((attempt + 1))
	sleep 5
done
