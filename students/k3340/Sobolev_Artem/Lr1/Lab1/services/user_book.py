from sqlalchemy.ext.asyncio import AsyncSession

from core.cruds import book as book_crud
from core.cruds import user_book as user_book_crud
from core.models.user_book import UserBook


class UserBookNotFoundError(Exception):
    pass


class UserBookConflictError(Exception):
    pass


class UserBookBookNotFoundError(Exception):
    pass


class UserBookForbiddenError(Exception):
    pass


async def search_library(
    session: AsyncSession,
    *,
    search: str | None = None,
    genre_id: int | None = None,
    owner_id: int | None = None,
    exclude_owner_id: int | None = None,
    available_only: bool | None = True,
) -> list[UserBook]:
    return await user_book_crud.get_user_books(
        session,
        owner_id=owner_id,
        exclude_owner_id=exclude_owner_id,
        available_only=available_only,
        genre_id=genre_id,
        search=search,
    )


async def get_user_book_or_raise(
    session: AsyncSession,
    user_book_id: int,
) -> UserBook:
    user_book = await user_book_crud.get_user_book_by_id(session, user_book_id)
    if user_book is None:
        raise UserBookNotFoundError(f"Library item with id={user_book_id} not found")
    return user_book


async def add_book_to_library(
    session: AsyncSession,
    *,
    owner_id: int,
    book_id: int,
    is_available: bool = True,
) -> UserBook:
    book = await book_crud.get_book_by_id(session, book_id)
    if book is None:
        raise UserBookBookNotFoundError(f"Book with id={book_id} not found")

    existing = await user_book_crud.get_user_book_by_owner_and_book(
        session,
        owner_id,
        book_id,
    )
    if existing is not None:
        raise UserBookConflictError("This book is already in the user's library")

    return await user_book_crud.create_user_book(
        session,
        owner_id=owner_id,
        book_id=book_id,
        is_available=is_available,
    )


async def update_library_item(
    session: AsyncSession,
    *,
    user_book_id: int,
    owner_id: int,
    user_book_data: dict,
) -> UserBook:
    user_book = await get_user_book_or_raise(session, user_book_id)
    if user_book.owner_id != owner_id:
        raise UserBookForbiddenError("You can manage only your own library items")

    return await user_book_crud.update_user_book(session, user_book, user_book_data)


async def remove_library_item(
    session: AsyncSession,
    *,
    user_book_id: int,
    owner_id: int,
) -> None:
    user_book = await get_user_book_or_raise(session, user_book_id)
    if user_book.owner_id != owner_id:
        raise UserBookForbiddenError("You can manage only your own library items")

    await user_book_crud.delete_user_book(session, user_book)
