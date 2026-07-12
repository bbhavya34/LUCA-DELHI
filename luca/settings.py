"""
Django settings for the Luca project.
"""

import os
from pathlib import Path

import dj_database_url


# ---------------------------------------------------------------------------
# Base directory
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def env_list(name: str, default: str = "") -> list[str]:
    """
    Convert a comma-separated environment variable into a Python list.
    """
    return [
        value.strip()
        for value in os.getenv(name, default).split(",")
        if value.strip()
    ]


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-development-only-change-me",
)

DEBUG = os.getenv(
    "DJANGO_DEBUG",
    "false",
).strip().lower() in {"1", "true", "yes", "on"}


ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost,.onrender.com,.railway.app",
)


CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    (
        "https://*.onrender.com,"
        "https://*.railway.app,"
        "https://*.ngrok-free.app,"
        "https://*.ngrok-free.dev,"
        "https://*.ngrok.io"
    ),
)


# Render automatically creates this environment variable.
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME:
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

    render_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"

    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)


# Railway support, in case you use Railway again.
RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN")

if RAILWAY_PUBLIC_DOMAIN:
    if RAILWAY_PUBLIC_DOMAIN not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

    railway_origin = f"https://{RAILWAY_PUBLIC_DOMAIN}"

    if railway_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_origin)


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Luca applications
    "accounts.apps.AccountsConfig",
    "dashboard.apps.DashboardConfig",
    "events.apps.EventsConfig",
    "promoters.apps.PromotersConfig",
    "guestlists.apps.GuestlistsConfig",
    "payments.apps.PaymentsConfig",
    "influencers.apps.InfluencersConfig",
]


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise must be directly after SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "luca.urls"


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "luca.wsgi.application"


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "60")),
            conn_health_checks=True,
        )
    }

elif DEBUG:
    # SQLite is only used for local development.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

else:
    raise RuntimeError(
        "DATABASE_URL is not configured. "
        "Add the PostgreSQL DATABASE_URL environment variable."
    )


# ---------------------------------------------------------------------------
# Custom user model
# ---------------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATIC_DIRECTORY = BASE_DIR / "static"

STATICFILES_DIRS = (
    [STATIC_DIRECTORY]
    if STATIC_DIRECTORY.exists()
    else []
)


# ---------------------------------------------------------------------------
# Uploaded media
# ---------------------------------------------------------------------------

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------------
# Storage configuration
# ---------------------------------------------------------------------------

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# ---------------------------------------------------------------------------
# Default primary key
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Reverse proxy and HTTPS settings
# ---------------------------------------------------------------------------

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

USE_X_FORWARDED_HOST = True


# Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv(
        "DJANGO_SECURE_SSL_REDIRECT",
        "true",
    ).strip().lower() in {"1", "true", "yes", "on"}

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False

    SECURE_HSTS_SECONDS = int(
        os.getenv(
            "DJANGO_SECURE_HSTS_SECONDS",
            "3600",
        )
    )

    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv(
        "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
        "true",
    ).strip().lower() in {"1", "true", "yes", "on"}

    SECURE_HSTS_PRELOAD = os.getenv(
        "DJANGO_SECURE_HSTS_PRELOAD",
        "false",
    ).strip().lower() in {"1", "true", "yes", "on"}

    X_FRAME_OPTIONS = "DENY"

    SECURE_CONTENT_TYPE_NOSNIFF = True

    SECURE_REFERRER_POLICY = "same-origin"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": (
                "[{levelname}] {asctime} "
                "{name}: {message}"
            ),
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },

    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },

    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },

        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
