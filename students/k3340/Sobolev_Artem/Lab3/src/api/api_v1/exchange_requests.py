from typing import Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth import get_current_active_auth_user, get_session
from api.api_v1.schemas import (
    ExchangeRequestCreate,
    ExchangeRequestResponse,
    ExchangeRequestStatusUpdate,
)
from api.api_v1.schemas.users import UserSchema
from services.exchange_request import (
    ExchangeRequestConflictError,
    ExchangeRequestForbiddenError,
    ExchangeRequestInvalidStateError,
    ExchangeRequestNotFoundError,
    create_exchange_request,
    delete_exchange_request,
    get_exchange_request_or_raise,
    list_exchange_requests,
    update_exchange_request_status,
)

router = APIRouter(prefix="/exchange-requests", tags=["Заявки на обмен"])


@router.get("/", response_model=list[ExchangeRequestResponse], summary="Получить список заявок на обмен")
async def get_my_exchange_requests(
    direction_filter: Literal["all", "sent", "received"] | None = Query(
        default=None,
        alias="направление",
        title="Направление",
        description="Какие заявки вернуть: все, отправленные или полученные.",
    ),
    direction: Literal["all", "sent", "received"] | None = Query(default=None, include_in_schema=False),
    request_status_filter: Literal["pending", "accepted", "rejected", "cancelled"]
    | None = Query(
        default=None,
        alias="статус",
        title="Статус заявки",
        description="Фильтр по статусу заявки.",
    ),
    request_status: Literal["pending", "accepted", "rejected", "cancelled"]
    | None = Query(default=None, alias="status", include_in_schema=False),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    resolved_direction = direction_filter if direction_filter is not None else direction
    if resolved_direction is None:
        resolved_direction = "all"
    resolved_status = (
        request_status_filter
        if request_status_filter is not None
        else request_status
    )

    return await list_exchange_requests(
        session,
        user_id=user.id,
        direction=resolved_direction,
        status=resolved_status,
    )


@router.get("/{request_id:int}", response_model=ExchangeRequestResponse, summary="Получить заявку на обмен")
async def get_exchange_request_details(
    request_id: int = Path(..., title="Идентификатор заявки", description="Числовой идентификатор заявки на обмен."),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        exchange_request = await get_exchange_request_or_raise(session, request_id)
    except ExchangeRequestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if user.id not in {exchange_request.requester_id, exchange_request.owner_id}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this exchange request",
        )

    return exchange_request


@router.post(
    "/",
    response_model=ExchangeRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заявку на обмен",
)
async def create_exchange_request_endpoint(
    request_in: ExchangeRequestCreate = Body(
        ...,
        title="Данные заявки на обмен",
        description="Идентификатор книги пользователя и сообщение к заявке.",
    ),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        return await create_exchange_request(
            session,
            requester_id=user.id,
            user_book_id=request_in.user_book_id,
            message=request_in.message,
        )
    except ExchangeRequestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ExchangeRequestForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ExchangeRequestConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ExchangeRequestInvalidStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{request_id:int}/status",
    response_model=ExchangeRequestResponse,
    summary="Изменить статус заявки на обмен",
)
async def update_exchange_request_status_endpoint(
    request_id: int = Path(..., title="Идентификатор заявки", description="Числовой идентификатор заявки на обмен."),
    request_in: ExchangeRequestStatusUpdate = Body(
        ...,
        title="Новый статус заявки",
        description="Новый статус заявки на обмен.",
    ),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        return await update_exchange_request_status(
            session,
            request_id=request_id,
            actor_id=user.id,
            status=request_in.status,
        )
    except ExchangeRequestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ExchangeRequestForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ExchangeRequestInvalidStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete("/{request_id:int}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить заявку на обмен")
async def delete_exchange_request_endpoint(
    request_id: int = Path(..., title="Идентификатор заявки", description="Числовой идентификатор заявки на обмен."),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        await delete_exchange_request(
            session,
            request_id=request_id,
            actor_id=user.id,
        )
    except ExchangeRequestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ExchangeRequestForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ExchangeRequestInvalidStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
