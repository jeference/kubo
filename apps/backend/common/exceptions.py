"""Erros de domínio e o handler do DRF que os transforma em `{detail, code}`.

Regras de negócio e guards levantam estes erros nos services; as views ficam finas.
"""

from rest_framework import status


class DomainError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "domain_error"
    default_detail = "Não foi possível concluir a ação."

    def __init__(
        self, detail: str | None = None, code: str | None = None, extra: dict | None = None
    ):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        self.extra = extra or {}
        super().__init__(self.detail)


class IllegalTransition(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "illegal_transition"
    default_detail = "Esta ação não está disponível no estado atual."


class GuardFailed(DomainError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = "guard_failed"
    default_detail = "Condição necessária não atendida."


class ImmutableRecordError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "immutable_record"
    default_detail = "Este registro não pode ser alterado."


class CodeInvalid(DomainError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = "code_invalid"
    default_detail = "Código inválido ou expirado."


class ResourceNotFound(DomainError):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "not_found"
    default_detail = "Não encontrado."


class Conflict(DomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "conflict"
    default_detail = "Conflito com o estado atual."


class QuotaExceeded(DomainError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_code = "quota_exceeded"
    default_detail = "Limite do dia atingido."


class ServiceBusy(DomainError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = "service_busy"
    default_detail = "Serviço temporariamente indisponível. Tente de novo em instantes."


class UpstreamUnavailable(DomainError):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_code = "upstream_unavailable"
    default_detail = "Serviço externo indisponível."


def exception_handler(exc, context):
    from rest_framework.response import Response
    from rest_framework.views import exception_handler as drf_exception_handler

    if isinstance(exc, DomainError):
        return Response(
            {"detail": exc.detail, "code": exc.code, **exc.extra}, status=exc.status_code
        )
    return drf_exception_handler(exc, context)
