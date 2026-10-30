"""Domain exceptions + DRF exception handler mapping them to HTTP responses.

Services raise these; views stay thin. Same contract as razantti: {"detail", "code"}.
"""

from rest_framework import status


class DomainError(Exception):
    """Base for business-rule violations. Carries an HTTP status + machine code."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "domain_error"

    def __init__(self, detail: str | None = None, code: str | None = None):
        self.detail = detail or self.__class__.__doc__ or "Erro de domínio."
        self.code = code or self.default_code
        super().__init__(self.detail)


class NotFound(DomainError):
    """Recurso não encontrado."""

    status_code = status.HTTP_404_NOT_FOUND
    default_code = "not_found"


class InvalidImage(DomainError):
    """Arquivo enviado não é uma imagem válida."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = "invalid_image"


class UpstreamUnavailable(DomainError):
    """Serviço externo (ex.: Runware) indisponível ou com erro."""

    status_code = status.HTTP_502_BAD_GATEWAY
    default_code = "upstream_unavailable"


def exception_handler(exc, context):
    """Map DomainError -> structured JSON; defer everything else to DRF."""
    from rest_framework.response import Response
    from rest_framework.views import exception_handler as drf_exception_handler

    if isinstance(exc, DomainError):
        return Response({"detail": exc.detail, "code": exc.code}, status=exc.status_code)
    return drf_exception_handler(exc, context)
