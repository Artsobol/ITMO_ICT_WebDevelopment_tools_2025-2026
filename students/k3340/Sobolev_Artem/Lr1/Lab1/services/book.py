from sqlalchemy.ext.asyncio import AsyncSession

from core.cruds import book as book_crud
from core.cruds import genre as genre_crud
from core.models.book import Book
from services.user_book import add_book_to_library


class BookNotFoundError(Exception):
    pass


class BookGenreNotFoundError(Exception):
    pass


class BookAuthorsNotFoundError(Exception):
    pass


async def list_books(session: AsyncSession):
    return await book_crud.get_all_books(session)


async def get_book_or_raise(session: AsyncSession, book_id: int) -> Book:
    book = await book_crud.get_book_by_id(session, book_id)
    if book is None:
        raise BookNotFoundError(f"Book with id={book_id} not found")
    return book


async def _ensure_genre_exists(session: AsyncSession, genre_id: int) -> None:
    genre = await genre_crud.get_genre_by_id(session, genre_id)
    if genre is None:
        raise BookGenreNotFoundError(f"Genre with id={genre_id} not found")


async def _fetch_authors_or_raise(
    session: AsyncSession,
    author_ids: list[int],
) -> list:
    authors = await book_crud.get_authors_by_ids(session, author_ids)
    missing_ids = sorted(set(author_ids) - {author.id for author in authors})
    if missing_ids:
        raise BookAuthorsNotFoundError(f"Authors not found for ids={missing_ids}")
    return authors


async def create_book(session: AsyncSession, book_data: dict) -> Book:
    genre_id = book_data.get("genre_id")
    if genre_id is not None:
        await _ensure_genre_exists(session, genre_id)

    authors = await _fetch_authors_or_raise(session, book_data.get("author_ids") or [])

    payload = {
        "title": book_data["title"],
        "description": book_data.get("description"),
        "genre_id": genre_id,
    }
    return await book_crud.create_book(session, payload, authors)


async def create_book_for_owner(
    session: AsyncSession,
    *,
    owner_id: int,
    book_data: dict,
) -> Book:
    book = await create_book(session, book_data)
    await add_book_to_library(
        session,
        owner_id=owner_id,
        book_id=book.id,
        is_available=True,
    )
    return book


async def update_book(session: AsyncSession, book_id: int, book_data: dict) -> Book:
    book = await get_book_or_raise(session, book_id)

    if "genre_id" in book_data and book_data["genre_id"] is not None:
        await _ensure_genre_exists(session, book_data["genre_id"])

    authors = None
    if "author_ids" in book_data:
        authors = await _fetch_authors_or_raise(
            session,
            book_data["author_ids"] or [],
        )

    payload = dict(book_data)
    payload.pop("author_ids", None)
    return await book_crud.update_book(session, book, payload, authors=authors)


async def delete_book(session: AsyncSession, book_id: int) -> None:
    book = await get_book_or_raise(session, book_id)
    await book_crud.delete_book(session, book)
