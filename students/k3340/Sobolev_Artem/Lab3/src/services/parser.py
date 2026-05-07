import httpx
from pydantic import ValidationError

from api.api_v1.schemas import ParserRequest, ParserResponse
from core.config import settings


class ParserServiceUnavailableError(Exception):
    pass


class ParserServiceResponseError(Exception):
    pass


class ParserServiceRequestError(Exception):
    def __init__(self, status_code: int, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(str(detail))


def _extract_error_detail(response: httpx.Response):
    """Достаёт detail из ответа парсера, если сервис вернул ошибку"""
    try:
        payload = response.json()
    except ValueError:
        return "Parser service returned a non-JSON error response"

    if isinstance(payload, dict) and "detail" in payload:
        return payload["detail"]

    return payload


async def parse_url(request: ParserRequest) -> ParserResponse:
    """Вызывает внешний сервис парсера и валидирует его JSON-ответ"""
    try:
        async with httpx.AsyncClient(
            base_url=settings.parser.base_url,
            timeout=settings.parser.timeout_seconds,
        ) as client:
            response = await client.post(
                "/parse",
                json=request.model_dump(mode="json"),
            )
    except httpx.RequestError as exc:
        raise ParserServiceUnavailableError("Parser service is unavailable") from exc

    if response.is_error:
        raise ParserServiceRequestError(
            status_code=response.status_code,
            detail=_extract_error_detail(response),
        )

    try:
        payload = response.json()
        return ParserResponse.model_validate(payload)
    except (ValueError, ValidationError) as exc:
        raise ParserServiceResponseError(
            "Parser service returned an unexpected response"
        ) from exc
