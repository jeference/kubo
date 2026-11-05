from django.db import models

from common.models import BaseModel


class IntegrationCredential(BaseModel):
    """Token OAuth renovável de um fornecedor, criptografado em repouso."""

    provider = models.CharField(max_length=32, unique=True)
    access_token_encrypted = models.TextField()
    refresh_token_encrypted = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
