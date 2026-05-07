from celery.result import AsyncResult
from kombu.exceptions import OperationalError
from pydantic import ValidationError

from tasks.parser_tasks import parse_url_task

from api.api_v1.schemas import (
    ParserRequest,
    ParserResponse,
    ParserTaskAcceptedResponse,
    ParserTaskStatusResponse,
)
from celery_app import celery_app


class ParserQueueUnavailableError(Exception):
    pass


def queue_parse_task(request: ParserRequest) -> ParserTaskAcceptedResponse:
    """Ставит задачу парсинга в Celery и возвращает идентификатор задачи."""
    try:
        task = parse_url_task.delay(str(request.url))
    except OperationalError as exc:
        raise ParserQueueUnavailableError("Celery queue is unavailable") from exc

    return ParserTaskAcceptedResponse(
        task_id=task.id,
        status=task.status,
        message="Parsing task has been queued",
    )


def get_parse_task_status(task_id: str) -> ParserTaskStatusResponse:
    """Читает статус и результат задачи парсинга из Celery backend."""
    try:
        task = AsyncResult(task_id, app=celery_app)
        task_status = task.status
        task_ready = task.ready()
        task_successful = task.successful()
    except OperationalError as exc:
        raise ParserQueueUnavailableError("Celery result backend is unavailable") from exc

    result = None
    error = None

    if task_successful:
        try:
            result = ParserResponse.model_validate(task.result)
        except ValidationError:
            error = "Celery task returned an unexpected payload"
    elif task_status == "FAILURE":
        error = str(task.result)

    return ParserTaskStatusResponse(
        task_id=task_id,
        status=task_status,
        ready=task_ready,
        successful=task_successful,
        result=result,
        error=error,
    )
