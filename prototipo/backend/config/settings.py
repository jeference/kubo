"""Django settings for the Kubo prototype — single module, env-driven.

Mirrors razantti's setup (django-environ + DRF + ports/adapters), scaled down:
no auth, no database models, files live in MEDIA_ROOT.
"""

from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

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
RUNWARE_IMAGE_MODEL = env("RUNWARE_IMAGE_MODEL", default="runware:400@2")  # FLUX.2 [klein] 9B
RUNWARE_3D_MODEL = env("RUNWARE_3D_MODEL", default="microsoft:trellis-2@4b")
# Quality/cost trade-off for the 3D preview. Costs are estimates (Runware bills by compute).
# Omitted params use Trellis defaults: 12 steps per stage, 500k faces.
TRELLIS_PRESETS = {
    # ~US$0.01, ~35-40s
    "low": {"resolution": 1024, "textureSize": 2048, "decimationTarget": 200000},
    # ~US$0.02, ~50-60s — more steps where they show most (shape), plus the detail
    # that low's decimation throws away.
    "medium": {
        "resolution": 1024,
        "textureSize": 2048,
        "decimationTarget": 350000,
        "sparseStructure": {"steps": 20},
        "shapeSlat": {"steps": 20},
        "texSlat": {"steps": 16},
    },
    # ~US$0.05-0.08, ~1-2min
    "high": {
        "resolution": 1536,
        "textureSize": 4096,
        "decimationTarget": 500000,
        "sparseStructure": {"steps": 30},
        "shapeSlat": {"steps": 30},
        "texSlat": {"steps": 24},
    },
}
TRELLIS_PRESET = env("TRELLIS_PRESET", default="low")
if TRELLIS_PRESET not in TRELLIS_PRESETS:
    raise ImproperlyConfigured(
        f"TRELLIS_PRESET={TRELLIS_PRESET!r}; use one of {', '.join(TRELLIS_PRESETS)}."
    )
TRELLIS_SETTINGS = TRELLIS_PRESETS[TRELLIS_PRESET]

MAX_PRINT_COLORS = 4
# Colors we have PLA filament for: name sent to the image model -> hex. Starting values
# are the common PLA colors; replace them with the real stock.
FILAMENT_COLORS = {
    "white": "#FFFFFF",
    "black": "#000000",
    "gray": "#8E9089",
    "red": "#C12E1F",
    "orange": "#FF6A13",
    "yellow": "#F4EE2A",
    "green": "#00AE42",
    "blue": "#0A2989",
    "purple": "#5E43B7",
    "pink": "#F5547C",
    "brown": "#9D432C",
    "beige": "#F7E6DE",
}
# Opens every prompt that produces a 2D image; at the end of the prompt, GPT Image 2 kept the
# off-list colors of requests and references. Tested 2026-11-02, one image per case: off-list
# colors were replaced in 3 of 4 cases, but only 1 of 6 images stayed within the limit, so
# this lowers the color count without guaranteeing it. No braces: templates go through .format().
_COLOR_RULE = (
    "This figurine is 3D printed, and only these filament colors exist: "
    + ", ".join(f"{name} ({hex_code})" for name, hex_code in FILAMENT_COLORS.items())
    + f". No other color can be printed. Use at most {MAX_PRINT_COLORS} of them on the whole "
    "figurine, counting the base and small details such as eyes, mouth and buttons. Do not "
    "reproduce colors from the request or the reference that are not on the list, such as "
    "turquoise, teal, gold, tan or light blue: repaint them in the closest listed color, "
    "even if that changes how it looks. Each part is one uniform matte color but stays a "
    "sculpted 3D form with volume, never a flat drawing. The white background does not count "
    "as a color. Do not draw the list, color swatches or any text.\n\n"
)

GENERATION = {
    "IMAGES_PER_PROMPT": 1,
    "IMAGE_SIZE": 1024,
    # Wraps the user's description to match the 2D references of Jujubit/Tripo, tuned
    # against 18 of their images (2026-10-31): a sculpted figurine look (fur and hair
    # as solid shapes, not strands), the whole object centered, and a
    # near-white background (#FDFDFD; theirs is #FCFCFC). FLUX.2 [klein] overreacts to
    # color words: "vivid"/"bright" turn objects rainbow, "natural" goes sepia,
    # "pristine" drains color; "studio lighting" adds a gray vignette.
    # Placeholders: {prompt} and {prompt_lower}.
    "PROMPT_TEMPLATE": (
        _COLOR_RULE + "{prompt}, as a detailed 3D figurine, shown whole, centered and filling "
        "the frame, isolated on a plain white background"
    ),
    # Sent with the current image as reference. Tested 2026-11-01: vague requests ("make it
    # prettier") otherwise lose the white background, which the 3D step relies on.
    # Placeholder: {instruction}.
    "EDIT_PROMPT_TEMPLATE": (
        _COLOR_RULE
        + "{instruction}. Keep everything else exactly the same, on a plain white background"
    ),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
