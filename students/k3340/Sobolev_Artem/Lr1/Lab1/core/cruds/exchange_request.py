from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.book import Book
from core.models.exchange_request import ExchangeRequest
from core.models.user import User
from core.models.user_book import UserBook


def _exchange_request_load_options():
    return (
        selectinload(ExchangeRequest.requester).selectinload(User.profile),
        selectinload(ExchangeRequest.owner).selectinload(User.profile),
        selectinload(ExchangeRequest.user_book)
        .selectinload(UserBook.owner)
        .selectinload(User.profile),
        selectinload(ExchangeRequest.user_book)
        .selectinload(UserBook.book)
        .selectinload(Book.genre),
        selectinload(ExchangeRequest.user_book)
        .selectinload(UserBook.book)
        .selectinload(Book.authors),
    )


async def get_exchange_request_by_id(
    session: AsyncSession,
    request_id: int,
) -> ExchangeRequest | None:
    stmt = (
        select(ExchangeRequest)
        .options(*_exchange_request_load_options())
        .where(ExchangeRequest.id == request_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_exchange_requests_for_user(
    session: AsyncSession,
    user_id: int,
    *,
    direction: str = "all",
    status: str | None = None,
) -> list[ExchangeRequest]:
    stmt = select(ExchangeRequest).options(*_exchange_request_load_options())

    if direction == "sent":
        stmt = stmt.where(ExchangeRequest.requester_id == user_id)
    elif direction == "received":
        stmt = stmt.where(ExchangeRequest.owner_id == user_id)
    else:
        stmt = stmt.where(
            (ExchangeRequest.requester_id == user_id)
            | (ExchangeRequest.owner_id == user_id)
        )

    if status is not None:
        stmt = stmt.where(ExchangeRequest.status == status)

    stmt = stmt.order_by(
        ExchangeRequest.created_at.desc(),
        ExchangeRequest.id.desc(),
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_pending_exchange_request(
    session: AsyncSession,
    requester_id: int,
    user_book_id: int,
) -> ExchangeRequest | None:
    stmt = (
        select(ExchangeRequest)
        .options(*_exchange_request_load_options())
        .where(
            ExchangeRequest.requester_id == requester_id,
            ExchangeRequest.user_book_id == user_book_id,
            ExchangeRequest.status == "pending",
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_exchange_request(
    session: AsyncSession,
    *,
    requester_id: int,
    owner_id: int,
    user_book_id: int,
    message: str | None = None,
) -> ExchangeRequest:
    exchange_request = ExchangeRequest(
        requester_id=requester_id,
        owner_id=owner_id,
        user_book_id=user_book_id,
        message=message,
        status="pending",
    )
    session.add(exchange_request)
    await session.commit()
    return await get_exchange_request_by_id(session, exchange_request.id)


async def update_exchange_request_status(
    session: AsyncSession,
    exchange_request: ExchangeRequest,
    status: str,
) -> ExchangeRequest:
    exchange_request.status = status
    await session.commit()
    return await get_exchange_request_by_id(session, exchange_request.id)


async def accept_exchange_request(
    session: AsyncSession,
    exchange_request: ExchangeRequest,
) -> ExchangeRequest:
    exchange_request.status = "accepted"
    exchange_request.user_book.is_available = False

    stmt = (
        update(ExchangeRequest)
        .where(
            ExchangeRequest.user_book_id == exchange_request.user_book_id,
            ExchangeRequest.id != exchange_request.id,
            ExchangeRequest.status == "pending",
        )
        .values(status="rejected")
    )
    await session.execute(stmt)
    await session.commit()
    return await get_exchange_request_by_id(session, exchange_request.id)


async def delete_exchange_request(
    session: AsyncSession,
    exchange_request: ExchangeRequest,
) -> None:
    await session.delete(exchange_request)
    await session.commit()
