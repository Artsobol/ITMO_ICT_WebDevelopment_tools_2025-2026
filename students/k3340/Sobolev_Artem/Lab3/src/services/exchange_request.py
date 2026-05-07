from sqlalchemy.ext.asyncio import AsyncSession

from core.cruds import exchange_request as exchange_request_crud
from core.models.exchange_request import ExchangeRequest
from services.user_book import UserBookNotFoundError, get_user_book_or_raise


class ExchangeRequestNotFoundError(Exception):
    pass


class ExchangeRequestConflictError(Exception):
    pass


class ExchangeRequestForbiddenError(Exception):
    pass


class ExchangeRequestInvalidStateError(Exception):
    pass


async def list_exchange_requests(
    session: AsyncSession,
    *,
    user_id: int,
    direction: str = "all",
    status: str | None = None,
) -> list[ExchangeRequest]:
    return await exchange_request_crud.get_exchange_requests_for_user(
        session,
        user_id,
        direction=direction,
        status=status,
    )


async def get_exchange_request_or_raise(
    session: AsyncSession,
    request_id: int,
) -> ExchangeRequest:
    exchange_request = await exchange_request_crud.get_exchange_request_by_id(
        session,
        request_id,
    )
    if exchange_request is None:
        raise ExchangeRequestNotFoundError(
            f"Exchange request with id={request_id} not found"
        )
    return exchange_request


async def create_exchange_request(
    session: AsyncSession,
    *,
    requester_id: int,
    user_book_id: int,
    message: str | None = None,
) -> ExchangeRequest:
    try:
        user_book = await get_user_book_or_raise(session, user_book_id)
    except UserBookNotFoundError as exc:
        raise ExchangeRequestNotFoundError(
            f"Library item with id={user_book_id} not found"
        ) from exc

    if user_book.owner_id == requester_id:
        raise ExchangeRequestForbiddenError("You cannot request your own book")

    if not user_book.is_available:
        raise ExchangeRequestInvalidStateError("This book is not available for exchange")

    existing = await exchange_request_crud.get_pending_exchange_request(
        session,
        requester_id=requester_id,
        user_book_id=user_book_id,
    )
    if existing is not None:
        raise ExchangeRequestConflictError("A pending exchange request already exists")

    return await exchange_request_crud.create_exchange_request(
        session,
        requester_id=requester_id,
        owner_id=user_book.owner_id,
        user_book_id=user_book_id,
        message=message,
    )


async def update_exchange_request_status(
    session: AsyncSession,
    *,
    request_id: int,
    actor_id: int,
    status: str,
) -> ExchangeRequest:
    exchange_request = await get_exchange_request_or_raise(session, request_id)

    if exchange_request.status != "pending":
        raise ExchangeRequestInvalidStateError(
            f"Only pending requests can be updated, current status={exchange_request.status!r}"
        )

    if status in {"accepted", "rejected"} and exchange_request.owner_id != actor_id:
        raise ExchangeRequestForbiddenError(
            "Only the book owner can accept or reject a request"
        )

    if status == "cancelled" and exchange_request.requester_id != actor_id:
        raise ExchangeRequestForbiddenError(
            "Only the requester can cancel a request"
        )

    if status == "accepted":
        if not exchange_request.user_book.is_available:
            raise ExchangeRequestInvalidStateError(
                "This book is no longer available for exchange"
            )
        return await exchange_request_crud.accept_exchange_request(
            session,
            exchange_request,
        )

    return await exchange_request_crud.update_exchange_request_status(
        session,
        exchange_request,
        status,
    )


async def delete_exchange_request(
    session: AsyncSession,
    *,
    request_id: int,
    actor_id: int,
) -> None:
    exchange_request = await get_exchange_request_or_raise(session, request_id)

    if actor_id not in {exchange_request.requester_id, exchange_request.owner_id}:
        raise ExchangeRequestForbiddenError(
            "You do not have access to this exchange request"
        )

    if exchange_request.status == "accepted":
        raise ExchangeRequestInvalidStateError(
            "Accepted exchange requests cannot be deleted"
        )

    await exchange_request_crud.delete_exchange_request(session, exchange_request)
