"""Criptografia de dados pessoais em repouso (CPF, token de acompanhamento)."""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


def _fernet() -> Fernet:
    key = settings.FIELD_ENCRYPTION_KEY
    if not key:  # Só em DEBUG: as configurações exigem a chave em produção.
        key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
    return Fernet(key)


def encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return _fernet().decrypt(value.encode()).decode()


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
