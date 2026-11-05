"""Worker de geração: consome `ProviderTask` com `FOR UPDATE SKIP LOCKED`.

Cada tarefa é pega com uma concessão de tempo (`locked_until`). Se o processo morrer, a
concessão vence e outro worker assume. O 3D é assíncrono: envia, passa para `waiting_provider`
e consulta de tempos em tempos, liberando a thread entre as consultas.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import requests
import structlog
from django.conf import settings
from django.db import close_old_connections, transaction
from django.db.models import Q
from django.utils import timezone

from common.alerts import alert
from common.fsm import apply_transition
from creations import costing, glb, quota
from creations.fsm import CREATION_FSM
from creations.models import Creation, ImageVersion, Model3D, ProviderTask
from creations.services import plain_background
from integrations.ports import (
    ContentRefused,
    ProviderPermanentError,
    ProviderTemporaryError,
    get_image_generation_port,
    get_model_3d_port,
)
from media import services as media
from media.models import Asset

_DOWNLOAD_TIMEOUT_SECONDS = 120
_IMAGE_KINDS = (
    ProviderTask.Kind.TEXT_TO_IMAGE,
    ProviderTask.Kind.PHOTO_TO_IMAGE,
    ProviderTask.Kind.IMAGE_EDIT,
)
_REFUSED_MESSAGE = (
    "Não conseguimos gerar essa imagem porque ela esbarrou nas regras de conteúdo. Personagens "
    "e marcas conhecidos, nudez e violência costumam ser recusados. Tente descrever de outro jeito."
)
_FAILED_MESSAGE = "Não conseguimos gerar agora. Tente de novo."
_NO_TEXTURE_MESSAGE = "O modelo saiu sem cor. Tente gerar de novo."
_TIMEOUT_MESSAGE = "A geração demorou demais. Tente de novo."

log = structlog.get_logger(__name__)


class _NoTexture(Exception):
    pass


def claim_task() -> ProviderTask | None:
    """Pega a próxima tarefa livre: na fila, ou com a concessão vencida."""
    now = timezone.now()
    lease = timedelta(seconds=settings.BUSINESS["TASK_LEASE_SECONDS"])
    with transaction.atomic():
        task = (
            ProviderTask.objects.select_for_update(skip_locked=True)
            .filter(
                Q(status=ProviderTask.Status.QUEUED)
                | Q(
                    status__in=(
                        ProviderTask.Status.RUNNING,
                        ProviderTask.Status.WAITING_PROVIDER,
                    )
                ),
                Q(next_attempt_at__isnull=True) | Q(next_attempt_at__lte=now),
                Q(locked_until__isnull=True) | Q(locked_until__lte=now),
            )
            .order_by("next_attempt_at", "created_at")
            .first()
        )
        if task is None:
            return None
        task.locked_until = now + lease
        task.started_at = task.started_at or now
        if task.status == ProviderTask.Status.QUEUED:
            task.status = ProviderTask.Status.RUNNING
        task.save(update_fields=["locked_until", "started_at", "status", "updated_at"])
    return task


def run_task(task: ProviderTask) -> None:
    structlog.contextvars.bind_contextvars(task_id=str(task.globalid), kind=task.kind)
    try:
        if task.kind in _IMAGE_KINDS:
            _run_image(task)
        else:
            _run_model(task)
    except ContentRefused as exc:
        _fail(task, code="content_refused", message=_REFUSED_MESSAGE, detail=str(exc))
    except _NoTexture:
        _retry_or_fail(task, code="model_without_texture", message=_NO_TEXTURE_MESSAGE)
    except (ProviderTemporaryError, requests.RequestException) as exc:
        _retry_or_fail(task, code="provider_unavailable", message=_FAILED_MESSAGE, detail=str(exc))
    except ProviderPermanentError as exc:
        _fail(task, code="provider_error", message=_FAILED_MESSAGE, detail=str(exc))
    except Exception as exc:
        log.exception("task_crashed")
        alert("generation_task_crashed", task_id=str(task.globalid), error=str(exc)[:200])
        _fail(task, code="internal_error", message=_FAILED_MESSAGE, detail=str(exc))
    finally:
        structlog.contextvars.unbind_contextvars("task_id", "kind")


def _is_cancelled(task: ProviderTask) -> bool:
    return (
        ProviderTask.objects.filter(pk=task.pk).values_list("status", flat=True).first()
        == ProviderTask.Status.CANCELLED
    )


def _record_cost(task: ProviderTask, cost: float | None) -> None:
    if cost is not None:
        task.cost_usd = Decimal(str(cost))


def _run_image(task: ProviderTask) -> None:
    port = get_image_generation_port()
    task.provider = port.provider
    task.model_name = port.model_name
    task.attempts += 1
    task.save(update_fields=["provider", "model_name", "attempts", "updated_at"])

    size = settings.BUSINESS["IMAGE_SIZE"]
    creation = task.creation
    if task.kind == ProviderTask.Kind.TEXT_TO_IMAGE:
        result = port.generate(prompt=task.rendered_prompt, size=size)
    else:
        if task.kind == ProviderTask.Kind.PHOTO_TO_IMAGE:
            source_asset = creation.input.photo
        else:
            source_asset = task.source_version.asset
        result = port.edit(image=media.read(source_asset), prompt=task.rendered_prompt, size=size)

    _record_cost(task, result.cost_usd)
    if _is_cancelled(task):
        # O provedor já cobrou: guarda o custo e descarta o resultado (RN-08).
        ProviderTask.objects.filter(pk=task.pk).update(cost_usd=task.cost_usd)
        return

    asset = media.store(data=result.data, kind=Asset.Kind.IMAGE, mime="image/png")
    plain = plain_background(result.data)
    source_plain = task.source_version.has_plain_background if task.source_version else True
    origin = {
        ProviderTask.Kind.TEXT_TO_IMAGE: ImageVersion.Origin.TEXT,
        ProviderTask.Kind.PHOTO_TO_IMAGE: ImageVersion.Origin.PHOTO,
        ProviderTask.Kind.IMAGE_EDIT: ImageVersion.Origin.EDIT,
    }[task.kind]

    with transaction.atomic():
        locked = Creation.objects.select_for_update().get(pk=creation.pk)
        number = locked.versions.count() + 1
        version = ImageVersion.objects.create(
            creation=locked,
            parent=task.source_version,
            number=number,
            origin=origin,
            instruction=task.instruction,
            asset=asset,
            task=task,
            has_plain_background=plain,
            background_lost=source_plain and not plain,
        )
        _succeed(task)
        if task.kind != ProviderTask.Kind.IMAGE_EDIT:
            locked.current_version = version
            locked.save(update_fields=["current_version", "updated_at"])
            apply_transition(instance=locked, fsm=CREATION_FSM, event="image_ready")


def _run_model(task: ProviderTask) -> None:
    port = get_model_3d_port()
    if not task.external_id:
        task.provider = port.provider
        task.model_name = port.model_name
        task.attempts += 1
        task.external_id = port.submit(image=media.read(task.source_version.asset))
        task.status = ProviderTask.Status.WAITING_PROVIDER
        _schedule_poll(task)
        return

    limit = timedelta(seconds=settings.BUSINESS["MODEL_TIMEOUT_SECONDS"])
    if timezone.now() - task.started_at > limit:
        _fail(task, code="timeout", message=_TIMEOUT_MESSAGE)
        return

    status = port.get(external_id=task.external_id)
    if status.status == "processing":
        _schedule_poll(task)
        return
    if status.status == "refused":
        raise ContentRefused(status.error)
    if status.status != "success":
        raise ProviderTemporaryError(status.error or "Falha no provedor.")

    _record_cost(task, status.cost_usd)
    data = status.file_bytes or _download(status.file_url)
    if not glb.has_texture(data):
        raise _NoTexture()
    asset = media.store(data=data, kind=Asset.Kind.MODEL, mime="model/gltf-binary")
    # Medir é pesado: fica fora da transação, para não segurar a linha da criação.
    measure = costing.measure_mesh(data)

    with transaction.atomic():
        locked = Creation.objects.select_for_update().get(pk=task.creation_id)
        model = Model3D.objects.create(
            creation=locked,
            source_version=task.source_version,
            asset=asset,
            task=task,
            triangles=glb.triangle_count(data),
            has_texture=True,
        )
        costing.apply_estimates(model=model, measure=measure)
        _succeed(task)
        locked.current_model = model
        locked.save(update_fields=["current_model", "updated_at"])
        apply_transition(instance=locked, fsm=CREATION_FSM, event="model_ready")


def _download(url: str) -> bytes:
    response = requests.get(url, timeout=_DOWNLOAD_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.content


def _schedule_poll(task: ProviderTask) -> None:
    task.next_attempt_at = timezone.now() + timedelta(
        seconds=settings.BUSINESS["MODEL_POLL_SECONDS"]
    )
    task.locked_until = None
    task.save(
        update_fields=[
            "provider",
            "model_name",
            "attempts",
            "external_id",
            "status",
            "next_attempt_at",
            "locked_until",
            "updated_at",
        ]
    )


def _succeed(task: ProviderTask) -> None:
    task.status = ProviderTask.Status.SUCCEEDED
    task.finished_at = timezone.now()
    task.locked_until = None
    task.save(
        update_fields=[
            "status",
            "finished_at",
            "locked_until",
            "cost_usd",
            "external_id",
            "provider",
            "model_name",
            "attempts",
            "updated_at",
        ]
    )
    quota.consume(task)


def _retry_or_fail(task: ProviderTask, *, code: str, message: str, detail: str = "") -> None:
    if task.attempts >= settings.BUSINESS["TASK_MAX_ATTEMPTS"]:
        _fail(task, code=code, message=message, detail=detail)
        return
    if _is_cancelled(task):
        return
    delay = 2**task.attempts
    task.status = ProviderTask.Status.QUEUED
    task.external_id = ""
    task.next_attempt_at = timezone.now() + timedelta(seconds=delay)
    task.locked_until = None
    task.error_code = code
    task.error_message = detail[:500]
    task.save(
        update_fields=[
            "status",
            "external_id",
            "next_attempt_at",
            "locked_until",
            "error_code",
            "error_message",
            "updated_at",
        ]
    )
    log.info("task_retry_scheduled", code=code, delay=delay)


def _fail(task: ProviderTask, *, code: str, message: str, detail: str = "") -> None:
    if _is_cancelled(task):
        return
    task.status = ProviderTask.Status.FAILED
    task.finished_at = timezone.now()
    task.locked_until = None
    task.error_code = code
    task.error_message = (detail or message)[:500]
    with transaction.atomic():
        task.save(
            update_fields=[
                "status",
                "finished_at",
                "locked_until",
                "error_code",
                "error_message",
                "attempts",
                "external_id",
                "provider",
                "model_name",
                "updated_at",
            ]
        )
        quota.release(task)
        if task.kind == ProviderTask.Kind.IMAGE_EDIT:
            return
        creation = Creation.objects.select_for_update().get(pk=task.creation_id)
        event = "model_failed" if task.kind == ProviderTask.Kind.IMAGE_TO_MODEL else "image_failed"
        creation.last_error_code = code
        creation.last_error_message = message
        creation.save(update_fields=["last_error_code", "last_error_message", "updated_at"])
        apply_transition(instance=creation, fsm=CREATION_FSM, event=event, payload={"code": code})


def run_once() -> bool:
    task = claim_task()
    if task is None:
        return False
    run_task(task)
    return True


def reconcile_stuck_tasks() -> int:
    """Tarefas sem progresso muito além do limite: encerra e devolve a cota."""
    limit = settings.BUSINESS["MODEL_TIMEOUT_SECONDS"] * 2
    cutoff = timezone.now() - timedelta(seconds=limit)
    stuck = ProviderTask.objects.filter(
        status__in=(ProviderTask.Status.RUNNING, ProviderTask.Status.WAITING_PROVIDER),
        started_at__lt=cutoff,
    ).filter(Q(locked_until__isnull=True) | Q(locked_until__lte=timezone.now()))
    count = 0
    for task in stuck:
        _fail(task, code="timeout", message=_TIMEOUT_MESSAGE)
        count += 1
    if count:
        alert("generation_tasks_stuck", count=count)
    return count


def close_connections() -> None:
    close_old_connections()
