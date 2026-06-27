# Lokal Booking Drammen

## Deploy to Render

This project includes `render.yaml` and `build.sh` for one-click Render deployment.

### 1. Push code to GitHub

The repository should include:

- `render.yaml`
- `build.sh`
- `requirements.txt` with production dependencies

### 2. Create service in Render

1. Open Render Dashboard.
2. Click `New` -> `Blueprint`.
3. Select your GitHub repository.
4. Render reads `render.yaml` and creates:
	- web service `lokal-booking-drammen`
	- PostgreSQL database `lokal-booking-drammen-db`

### 3. Environment variables

Configured in `render.yaml`:

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DJANGO_SECRET_KEY` auto-generated
- `DATABASE_URL` from Render PostgreSQL

Optional manual env vars:

- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`

### 4. Build/start commands

- Build: `./build.sh`
- Start: `gunicorn config.wsgi:application`

`build.sh` runs:

1. `pip install -r requirements.txt`
2. `python manage.py collectstatic --no-input`
3. `python manage.py migrate`
