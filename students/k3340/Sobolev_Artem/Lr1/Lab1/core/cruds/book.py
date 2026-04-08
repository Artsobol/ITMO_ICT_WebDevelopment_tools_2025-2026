from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.author import Author
from core.models.book import Book


async def get_all_books(session: AsyncSession) -> Sequence[Book]:
    stmt = (
        select(Book)
        .options(selectinload(Book.genre), selectinload(Book.authors))
        .order_by(Book.id)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_book_by_id(session: AsyncSession, book_id: int) -> Book | None:
    stmt = (
        select(Book)
        .options(selectinload(Book.genre), selectinload(Book.authors))
        .where(Book.id == book_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_authors_by_ids(session: AsyncSession, author_ids: list[int]) -> list[Author]:
    if not author_ids:
        return []
    stmt = select(Author).where(Author.id.in_(author_ids))
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_book(
    session: AsyncSession,
    book_data: dict,
    authors: list[Author],
) -> Book:
    book_obj = Book(**book_data)
    book_obj.authors = authors
    session.add(book_obj)
    await session.commit()
    return await get_book_by_id(session, book_obj.id)


async def update_book(
    session: AsyncSession,
    book: Book,
    book_data: dict,
    authors: list[Author] | None = None,
) -> Book:
    for field, value in book_data.items():
        setattr(book, field, value)

    if authors is not None:
        book.authors = authors

    await session.commit()
    return await get_book_by_id(session, book.id)


async def delete_book(session: AsyncSession, book: Book) -> None:
    await session.delete(book)
    await session.commit()
