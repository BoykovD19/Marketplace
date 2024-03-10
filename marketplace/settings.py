import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = ['*']

SECRET_KEY = env.str('SECRET_KEY')

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "minio_storage",
    "corsheaders",
    "drf_yasg",
    "django_filters",
    "integration",
    "accounts",
    "product",
    "warehouse",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "marketplace.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
}

WSGI_APPLICATION = "marketplace.wsgi.application"

AUTH_USER_MODEL = "accounts.User"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

SCHEMA = env.str("SCHEMA")

HOST = env.str("HOST")

EMAIL_RECOVERY_PAGE = env.str("EMAIL_RECOVERY_PAGE")

UNISENDER_TOKEN = env.str("UNISENDER_TOKEN")

UNISENDER_URL = env.str("UNISENDER_URL")

SENDER_NAME = env.str("SENDER_NAME")

SENDER_EMAIL = env.str("SENDER_EMAIL")

CODE_LENGTH = env.int("CODE_LENGTH")

SMS_CODE_LENGTH = env.str("SMS_CODE_LENGTH")

PASSWORD_LENGTH = env.int("PASSWORD_LENGTH")

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = '/static/'

STATIC_ROOT = './static_files/'

NUMBER_OF_PRODUCT_PHOTOS = env.int("NUMBER_OF_PRODUCT_PHOTOS")

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
MINIO_STORAGE_ENDPOINT = env.str('MINIO_STORAGE_ENDPOINT')
MINIO_STORAGE_ACCESS_KEY = env.str('MINIO_STORAGE_ACCESS_KEY')
MINIO_STORAGE_SECRET_KEY = env.str('MINIO_STORAGE_SECRET_KEY')
MINIO_STORAGE_USE_HTTPS = env.bool('MINIO_STORAGE_USE_HTTPS')
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = env.bool(
    'MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET'
)
MINIO_STORAGE_MEDIA_BUCKET_NAME = env.str('MINIO_STORAGE_MEDIA_BUCKET_NAME')
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = env.bool(
    'MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET'
)
MINIO_STORAGE_STATIC_BUCKET_NAME = env.str('MINIO_STORAGE_STATIC_BUCKET_NAME')
MINIO_STORAGE_MEDIA_URL = (
    f'{SCHEMA}{MINIO_STORAGE_ENDPOINT}/{MINIO_STORAGE_MEDIA_BUCKET_NAME}'
)
MINIO_STORAGE_STATIC_URL = (
    f'{SCHEMA}{MINIO_STORAGE_ENDPOINT}/{MINIO_STORAGE_STATIC_BUCKET_NAME}'
)
