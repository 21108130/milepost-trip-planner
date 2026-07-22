
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-key-change-in-production-1234567890",
)

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "trips",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "False") == "True"


REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "EXCEPTION_HANDLER": "trips.utils.exception_handler.custom_exception_handler",
}


OPENROUTESERVICE_API_KEY = os.environ.get("OPENROUTESERVICE_API_KEY", "")

# HOS (Hours of Service) constants for property-carrying drivers
HOS_MAX_DRIVING_HOURS = 11          # Max driving hours per shift
HOS_MAX_ON_DUTY_WINDOW = 14         # Max on-duty window per shift
HOS_MIN_OFF_DUTY_HOURS = 10         # Min consecutive off-duty hours required
HOS_BREAK_AFTER_HOURS = 8           # 30-min break required after this many driving hours
HOS_BREAK_DURATION_MINUTES = 30
HOS_CYCLE_MAX_HOURS = 70            # 70-hour / 8-day cycle
HOS_CYCLE_DAYS = 8
HOS_FUEL_INTERVAL_MILES = 1000
HOS_PICKUP_DURATION_HOURS = 1
HOS_DROPOFF_DURATION_HOURS = 1
HOS_AVERAGE_SPEED_MPH = 55
