from fastapi import APIRouter, Body, HTTPException, Path, status

from api.api_v1.schemas import (
    ParserRequest,
    ParserResponse,
    ParserTaskAcceptedResponse,
    ParserTaskStatusResponse,
)
from services.parser import (
    ParserServiceRequestError,
    ParserServiceResponseError,
    ParserServiceUnavailableError,
    parse_url,
)
from services.parser_queue import (
    ParserQueueUnavailableError,
    get_parse_task_status,
    queue_parse_task,
)

router = APIRouter(prefix="/parser", tags=["Парсер"])


@router.post(
    "/parse",
    response_model=ParserResponse,
    status_code=status.HTTP_200_OK,
    summary="Запустить парсер через отдельный сервис",
)
async def parse_url_endpoint(
    request: ParserRequest = Body(
        ...,
        title="Данные для парсинга",
        description="URL страницы книги, которую нужно отправить в отдельный сервис парсинга.",
    ),
):
    """Отправляет URL в отдельный HTTP-сервис парсера и возвращает его ответ"""
    try:
        return await parse_url(request)
    except ParserServiceRequestError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    except ParserServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ParserServiceResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.post(
    "/parse-async",
    response_model=ParserTaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Поставить парсинг в очередь Celery",
)
async def parse_url_async_endpoint(
    request: ParserRequest = Body(
        ...,
        title="Данные для асинхронного парсинга",
        description="URL страницы книги, которую нужно поставить в очередь на парсинг.",
    ),
):
    """Ставит задачу парсинга в очередь Celery и возвращает task_id"""
    try:
        return queue_parse_task(request)
    except ParserQueueUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get(
    "/tasks/{task_id}",
    response_model=ParserTaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить статус задачи парсинга",
)
async def get_parse_task_status_endpoint(
    task_id: str = Path(
        ...,
        title="Идентификатор задачи",
        description="Идентификатор задачи Celery, полученный при постановке в очередь.",
    ),
):
    """Возвращает текущий статус фоновой задачи парсинга"""
    try:
        return get_parse_task_status(task_id)
    except ParserQueueUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
