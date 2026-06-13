import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SEGURIDAD BASE
# =========================================================

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "solo-local-no-produccion",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"


ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost,192.168.7.250,192.168.100.21,192.168.7.210,138.36.238.175,www.ailonline.com.ar,ailonline.com.ar",
).split(",")


CSRF_TRUSTED_ORIGINS = os.environ.get(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://192.168.7.250,http://192.168.100.21,http://192.168.7.210,http://138.36.238.175,http://138.36.238.175:8001,http://138.36.238.175:8010,https://www.ailonline.com.ar,https://ailonline.com.ar",
).split(",")


# =========================================================
# APPS
# =========================================================

INSTALLED_APPS = [
    "calculadora",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise solo en producción (en desarrollo Django sirve estáticos directamente)
    *( ["whitenoise.middleware.WhiteNoiseMiddleware"] if not DEBUG else [] ),

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "glicemia.urls"


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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


WSGI_APPLICATION = "glicemia.wsgi.application"


# =========================================================
# BASE DE DATOS
# =========================================================
# SQLite para desarrollo / primera versión.
# Producción profesional recomendada: PostgreSQL.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# =========================================================
# VALIDADORES DE CONTRASEÑA
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# =========================================================
# LOCALIZACIÓN
# =========================================================

LANGUAGE_CODE = "es-ar"

TIME_ZONE = "America/Argentina/Cordoba"

USE_I18N = True
USE_TZ = True


# =========================================================
# LOGIN / LOGOUT
# =========================================================

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


# =========================================================
# SESIONES Y COOKIES
# =========================================================

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SESSION_COOKIE_AGE = 1800

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True


# =========================================================
# HTTPS
# =========================================================

USE_HTTPS = os.environ.get("USE_HTTPS", "False") == "True"

SESSION_COOKIE_SECURE = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / "staticfiles"

if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# =========================================================
# DEFAULTS
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================================================
# HEADERS DE SEGURIDAD
# =========================================================

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"


# =========================================================
# HTTPS EXTRA
# =========================================================

if USE_HTTPS:

    SECURE_SSL_REDIRECT = True

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True