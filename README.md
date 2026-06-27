# Lokal Booking Drammen

Lokal Booking Drammen is a fullstack Django booking application for local clubs, volunteer organizations, and small course providers.

The app replaces manual spreadsheets and email threads with a structured workflow for resource booking, approval, status tracking, and administration.

## What the project does

- Handles user authentication with role-based behavior (member and admin/staff).
- Lets members create, view, and cancel bookings.
- Lets admins approve/reject/edit bookings from a dashboard.
- Applies booking rules such as opening hours, booking horizon, max duration, cancellation deadline, and collision checks.
- Sends booking status emails via Django email backend.
- Exports bookings as CSV from admin dashboard.
- Supports free-licensed local images for a Drammen-themed landing page.

## Main features

### Member flow

- Login/logout.
- Create booking form.
- My bookings list.
- Cancel booking (with policy checks).

### Admin flow

- Dashboard statistics (total/pending/confirmed/canceled).
- Booking management list with filtering.
- Approve/reject/edit booking actions.
- CSV export.

## Tech stack

- Backend: Django
- Database (local): SQLite
- Database (production): PostgreSQL
- App server: Gunicorn
- Static files: WhiteNoise
- Deployment: Render (Blueprint with `render.yaml`)

## Project structure

```
lokal-booking-drammen/
	apps/
		accounts/
		resources/
		bookings/
		notifications/
		dashboard/
	config/
		settings/
			base.py
			development.py
			production.py
	templates/
	static/
	docs/
	render.yaml
	build.sh
```

## Local development

### 1. Create and activate virtual environment

Windows PowerShell:

```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run migrations

```
python manage.py migrate
```

### 4. Create admin user

```
python manage.py createsuperuser
```

### 5. Start development server

```
python manage.py runserver
```

App runs at `http://127.0.0.1:8000/`.

## Testing

Run all tests:

```
python manage.py test
```

## Images and attribution

To add real Drammen photos on home page, place files here:

- `static/img/drammen/photo-1.jpg`
- `static/img/drammen/photo-2.jpg`
- `static/img/drammen/photo-3.jpg`

If JPG files are missing, the app shows local SVG placeholders.

Only use free-licensed images. See:

- `docs/image-attribution.md`

## Deploy to Render

This repository includes `render.yaml` and `build.sh` for Blueprint deployment.

### 1. Deploy from GitHub

1. Open Render Dashboard.
2. Click `New` -> `Blueprint`.
3. Select this repository.
4. Render creates:
	 - web service `lokal-booking-drammen`
	 - PostgreSQL database `lokal-booking-drammen-db`

### 2. Environment variables

Configured in `render.yaml`:

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DJANGO_SECRET_KEY` (auto-generated)
- `DATABASE_URL` (from Render PostgreSQL)

Optional:

- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`

### 3. Build/start commands

- Build: `./build.sh`
- Start: `gunicorn config.wsgi:application`

`build.sh` runs:

1. `pip install -r requirements.txt`
2. `python manage.py collectstatic --no-input`
3. `python manage.py migrate`
