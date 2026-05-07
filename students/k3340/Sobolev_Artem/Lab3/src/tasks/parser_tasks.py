import asyncio

from celery_app import celery_app
from api.api_v1.schemas import ParserRequest
from core.config import settings
from services.parser import (
    ParserServiceRequestError,
    ParserServiceResponseError,
    ParserServiceUnavailableError,
    parse_url,
)


@celery_app.task(name="parser.parse_url")
def parse_url_task(url: str) -> dict:
    """Запускает парсинг одного URL через отдельный сервис parser."""
    request = ParserRequest(url=url)

    try:
        result = asyncio.run(parse_url(request))
    except ParserServiceRequestError as exc:
        raise RuntimeError(
            f"Parser service returned status {exc.status_code}: {exc.detail}"
        ) from exc
    except ParserServiceUnavailableError as exc:
        raise RuntimeError("Parser service is unavailable") from exc
    except ParserServiceResponseError as exc:
        raise RuntimeError(str(exc)) from exc

    return result.model_dump(mode="json")


@celery_app.task(name="parser.enqueue_periodic_parse_batch")
def enqueue_periodic_parse_batch() -> dict:
    """Периодически создаёт набор задач парсинга для URL из конфигурации."""
    task_ids: list[str] = []
    urls = settings.celery.get_periodic_parse_urls()

    for url in urls:
        task = parse_url_task.delay(url)
        task_ids.append(task.id)

    return {
        "queued_count": len(task_ids),
        "urls": urls,
        "task_ids": task_ids,
    }
