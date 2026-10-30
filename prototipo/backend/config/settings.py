"""Django settings for the Kubo prototype — single module, env-driven.

Mirrors razantti's setup (django-environ + DRF + ports/adapters), scaled down:
no auth, no database models, files live in MEDIA_ROOT.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, True),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# --- Applications ---
DJANGO_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
]
LOCAL_APPS = [
    "common",
    "integrations",
    "generation",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
    },
]

# No models in the prototype — SQLite only keeps Django happy.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "_media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Photos from the phone can be large.
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

# --- DRF ---
REST_FRAMEWORK = {
    # Prototype used by a single person locally: no auth, everything open.
    "DEFAULT_AUTHENTICATION_CLASSES": (),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "EXCEPTION_HANDLER": "common.exceptions.exception_handler",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# --- Integrations (ports/adapters) ---
# `integrations.adapters.runware_stub.StubGenerationAdapter` runs offline (no credits spent).
GENERATION_ADAPTER = env(
    "GENERATION_ADAPTER",
    default="integrations.adapters.runware.RunwareGenerationAdapter",
)
RUNWARE_API_KEY = env("RUNWARE_API_KEY", default="")
RUNWARE_IMAGE_MODEL = env("RUNWARE_IMAGE_MODEL", default="runware:100@1")  # FLUX.1 schnell
RUNWARE_3D_MODEL = env("RUNWARE_3D_MODEL", default="microsoft:trellis-2@4b")
TRELLIS_SETTINGS = env.json(
    "TRELLIS_SETTINGS",
    default={
        "resolution": 1024,
        # Default is 500k faces — too heavy for a browser preview.
        "decimationTarget": 200000,
        "textureSize": 2048,
    },
)

GENERATION = {
    "IMAGES_PER_PROMPT": 4,
    "IMAGE_SIZE": 1024,
    # Appended to every user prompt so outputs come out "printable-looking".
    "PROMPT_STYLE_SUFFIX": (
        "single object, collectible figurine, full view, centered, isolated on a plain "
        "white background, no text, soft studio lighting"
    ),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
