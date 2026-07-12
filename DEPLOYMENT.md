# LUCA deployment

## Required production configuration

Set the variables from `.env.example`. Generate a unique `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=false`, and use the exact public hostname and HTTPS origin for `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS`.

Use a managed PostgreSQL database through `DATABASE_URL`. SQLite is retained only as the local-development default.

## Build and start

Build command:

```sh
python -m pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

Start command:

```sh
gunicorn luca.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
```

Use `/health/` for platform health checks.

## Uploaded media

LUCA accepts event photos/videos, profile images, screenshots, and QR images. Production must mount persistent storage at `MEDIA_ROOT` or configure an object-storage backend before accepting uploads. Ephemeral application filesystems will lose uploaded media during deploys or restarts.

## Release checklist

```sh
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python manage.py collectstatic --noinput
python manage.py test
```

Create the first administrator using `python manage.py createsuperuser`. Confirm HTTPS, login/logout, an upload, and `/health/` after deployment. Back up PostgreSQL and uploaded media independently.
