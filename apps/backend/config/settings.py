"""Configuração do backend. Tudo que varia por ambiente vem de variáveis (django-environ)."""

from datetime import timedelta
from pathlib import Path

import environ
import structlog
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

DEBUG = env.bool("DJANGO_DEBUG", default=False)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me" if DEBUG else "")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY é obrigatória fora de DEBUG.")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "common",
    "audit",
    "accounts",
    "catalog",
    "media",
    "creations",
    "shipping",
    "orders",
    "payments",
    "fulfillment",
    "notifications",
    "analytics",
    "integrations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "common.middleware.RequestContextMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

DATABASES = {"default": env.db("DATABASE_URL", default="postgres://kubo@127.0.0.1:5433/kubo")}
DATABASES["default"]["ATOMIC_REQUESTS"] = False
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Throttles e o estado do stub precisam ser vistos por todos os processos: cache no banco.
# A tabela é criada por uma migração de `common`.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# --- API ---
NUM_PROXIES = env.int("NUM_PROXIES", default=1)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "accounts.authentication.VisitorAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("common.permissions.DenyAll",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.DefaultPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "common.exceptions.exception_handler",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "NUM_PROXIES": NUM_PROXIES,
    "DEFAULT_THROTTLE_RATES": {
        "visitor_create": "30/hour",
        "auth_register": "10/hour",
        "auth_login": "10/min",
        "auth_login_email": "10/min",
        "auth_refresh": "60/min",
        "auth_verify": "10/min",
        "auth_verify_email": "10/min",
        "auth_resend": "5/hour",
        "auth_resend_email": "5/hour",
        "auth_password_reset": "5/hour",
        "auth_password_reset_email": "5/hour",
        "auth_password_reset_confirm": "10/min",
        "auth_password_reset_confirm_email": "10/min",
        "generation_write": "60/hour",
        "shipping_quote": "30/min",
        "address_lookup": "30/min",
        "order_write": "20/min",
        "order_track": "30/min",
        "order_track_resend": "5/hour",
        "events": "240/min",
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Kubo API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_NAME_OVERRIDES": {
        "CreationStatusEnum": "creations.models.Creation.Status",
        "ProviderTaskStatusEnum": "creations.models.ProviderTask.Status",
        "ProviderTaskKindEnum": "creations.models.ProviderTask.Kind",
        "OrderStatusEnum": "orders.models.Order.Status",
        "ChargeStatusEnum": "payments.models.Charge.Status",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "USER_ID_FIELD": "globalid",
    "USER_ID_CLAIM": "user_id",
    "UPDATE_LAST_LOGIN": False,
}

# --- Regras de negócio configuráveis. Valores marcados [Proposta] no PRD ---
BUSINESS = {
    "ACCOUNT_CODE_TTL_MINUTES": 15,
    "ACCOUNT_CODE_RESEND_COOLDOWN_SECONDS": 60,
    # RN-04: limites por dia e por sessão ou conta.
    "QUOTA_PER_DAY": {"image": 10, "edit": 15, "model": 6},
    "QUOTA_PER_IP_PER_DAY": {"image": 40, "edit": 60, "model": 24},
    # RN-05: tarefas simultâneas.
    "MAX_ACTIVE_TASKS": 2,
    "MAX_ACTIVE_MODEL_TASKS": 1,
    # RN-06: teto global de gasto diário com IA. Sem custo informado, vale a estimativa.
    "DAILY_SPEND_CAP_USD": env.float("DAILY_SPEND_CAP_USD", default=30.0),
    "ESTIMATED_COST_USD": {"image": 0.02, "edit": 0.02, "model": 0.06},
    # Worker.
    "TASK_MAX_ATTEMPTS": 3,
    "TASK_LEASE_SECONDS": 150,
    "MODEL_TIMEOUT_SECONDS": 600,
    "MODEL_POLL_SECONDS": 2,
    "WORKER_THREADS": env.int("WORKER_THREADS", default=8),
    # Upload de foto e textos.
    "PHOTO_MAX_BYTES": 10 * 1024 * 1024,
    "IMAGE_SIZE": 1024,
    "TEXT_MAX_CHARS": 1000,
    "EDIT_MAX_CHARS": 200,
    # Compra.
    "MAX_ITEM_QUANTITY": 10,
    "PIX_EXPIRES_SECONDS": 30 * 60,
    "PIX_RENEWAL_WINDOW_HOURS": 24,
    "SHIPPING_QUOTE_TTL_MINUTES": 30,
    "PRODUCTION_DAYS": 7,  # RN-16
    "TERMS_VERSION": "2026-11",
    # URLs e retenção.
    "SIGNED_URL_TTL_SECONDS": 300,
    "PHOTO_RETENTION_DAYS": 90,
    "DELETED_CREATION_PURGE_DAYS": 30,
    "VISITOR_RETENTION_DAYS": 365,
}

INTERNAL_PARTNER_POSTAL_CODE = env("INTERNAL_PARTNER_POSTAL_CODE", default="01001000")
CONSUMER_APP_URL = env("CONSUMER_APP_URL", default="http://localhost:3000").rstrip("/")

# Chave Fernet. Em DEBUG, derivada da SECRET_KEY para o projeto subir sem configuração.
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY", default="")
if not FIELD_ENCRYPTION_KEY and not DEBUG:
    raise ImproperlyConfigured("FIELD_ENCRYPTION_KEY é obrigatória fora de DEBUG.")

# --- Adapters (ports). Padrão: fornecedores reais. Só os testes usam simulação ---
IMAGE_GENERATION_ADAPTER = env(
    "IMAGE_GENERATION_ADAPTER",
    default="integrations.adapters.runware.RunwareImageGenerationAdapter",
)
MODEL_3D_ADAPTER = env(
    "MODEL_3D_ADAPTER", default="integrations.adapters.runware.RunwareModel3DAdapter"
)
PAYMENT_GATEWAY_ADAPTER = env(
    "PAYMENT_GATEWAY_ADAPTER", default="integrations.adapters.abacatepay.AbacatePayAdapter"
)
SHIPPING_ADAPTER = env(
    "SHIPPING_ADAPTER", default="integrations.adapters.melhor_envio.MelhorEnvioAdapter"
)
ADDRESS_LOOKUP_ADAPTER = env(
    "ADDRESS_LOOKUP_ADAPTER", default="integrations.adapters.viacep.ViaCepAdapter"
)
MEDIA_STORAGE_ADAPTER = env(
    "MEDIA_STORAGE_ADAPTER", default="integrations.adapters.media_local.LocalMediaAdapter"
)
EMAIL_ADAPTER = env(
    "EMAIL_ADAPTER", default="integrations.adapters.email_console.ConsoleEmailAdapter"
)

# Runware.
RUNWARE_API_KEY = env("RUNWARE_API_KEY", default="")
RUNWARE_IMAGE_MODEL = env("RUNWARE_IMAGE_MODEL", default="openai:gpt-image@2")
RUNWARE_3D_MODEL = env("RUNWARE_3D_MODEL", default="microsoft:trellis-2@4b")
TRELLIS_PRESETS = {
    "low": {"resolution": 1024, "textureSize": 2048, "decimationTarget": 200000},
    "medium": {
        "resolution": 1024,
        "textureSize": 2048,
        "decimationTarget": 350000,
        "sparseStructure": {"steps": 20},
        "shapeSlat": {"steps": 20},
        "texSlat": {"steps": 16},
    },
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
    raise ImproperlyConfigured(f"TRELLIS_PRESET inválido: {TRELLIS_PRESET!r}.")
TRELLIS_SETTINGS = TRELLIS_PRESETS[TRELLIS_PRESET]

# AbacatePay.
ABACATE_PAY_BASE_URL = env("ABACATE_PAY_BASE_URL", default="https://api.abacatepay.com/v2")
ABACATE_PAY_API_KEY = env("ABACATE_PAY_API_KEY", default="")
ABACATE_PAY_WEBHOOK_SECRET = env("ABACATE_PAY_WEBHOOK_SECRET", default="")

# Melhor Envio.
MELHOR_ENVIO_BASE_URL = env("MELHOR_ENVIO_BASE_URL", default="https://sandbox.melhorenvio.com.br")
MELHOR_ENVIO_CLIENT_ID = env("MELHOR_ENVIO_CLIENT_ID", default="")
MELHOR_ENVIO_CLIENT_SECRET = env("MELHOR_ENVIO_CLIENT_SECRET", default="")
MELHOR_ENVIO_ACCESS_TOKEN = env("MELHOR_ENVIO_ACCESS_TOKEN", default="")
MELHOR_ENVIO_REFRESH_TOKEN = env("MELHOR_ENVIO_REFRESH_TOKEN", default="")
MELHOR_ENVIO_USER_AGENT = env("MELHOR_ENVIO_USER_AGENT", default="Kubo")
MELHOR_ENVIO_SERVICES = env("MELHOR_ENVIO_SERVICES", default="")

# Storage.
MEDIA_ROOT = env("MEDIA_ROOT", default=str(BASE_DIR / "_media"))
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")

# E-mail.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Kubo <nao-responda@exemplo.com>")

# --- Segurança em produção ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
if not DEBUG:
    SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# --- Logs: JSON em produção, legível em DEBUG, sem dados pessoais ---
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(colors=False)
        if DEBUG
        else structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
