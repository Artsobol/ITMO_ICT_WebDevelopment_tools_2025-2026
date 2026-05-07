from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.author import Author
from core.models.book import Book
from core.models.profile import Profile
from core.models.user import User
from core.models.user_book import UserBook


def _user_book_load_options():
    return (
        selectinload(UserBook.owner).selectinload(User.profile),
        selectinload(UserBook.book).selectinload(Book.genre),
        selectinload(UserBook.book).selectinload(Book.authors),
    )


async def get_user_book_by_id(
    session: AsyncSession,
    user_book_id: int,
) -> UserBook | None:
    stmt = (
        select(UserBook)
        .options(*_user_book_load_options())
        .where(UserBook.id == user_book_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_book_by_owner_and_book(
    session: AsyncSession,
    owner_id: int,
    book_id: int,
) -> UserBook | None:
    stmt = (
        select(UserBook)
        .options(*_user_book_load_options())
        .where(UserBook.owner_id == owner_id, UserBook.book_id == book_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_books(
    session: AsyncSession,
    *,
    owner_id: int | None = None,
    exclude_owner_id: int | None = None,
    available_only: bool | None = None,
    genre_id: int | None = None,
    search: str | None = None,
) -> list[UserBook]:
    stmt = (
        select(UserBook)
        .options(*_user_book_load_options())
        .join(UserBook.book)
        .join(UserBook.owner)
    )

    if owner_id is not None:
        stmt = stmt.where(UserBook.owner_id == owner_id)

    if exclude_owner_id is not None:
        stmt = stmt.where(UserBook.owner_id != exclude_owner_id)

    if available_only is not None:
        stmt = stmt.where(UserBook.is_available.is_(available_only))

    if genre_id is not None:
        stmt = stmt.where(Book.genre_id == genre_id)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.outerjoin(Book.authors).outerjoin(User.profile).where(
            or_(
                Book.title.ilike(pattern),
                Book.description.ilike(pattern),
                Author.name.ilike(pattern),
                User.username.ilike(pattern),
                Profile.full_name.ilike(pattern),
            )
        )

    stmt = stmt.order_by(UserBook.created_at.desc(), UserBook.id.desc()).distinct()
    result = await session.execute(stmt)
    return list(result.scalars().unique().all())


async def create_user_book(
    session: AsyncSession,
    owner_id: int,
    book_id: int,
    is_available: bool = True,
) -> UserBook:
    user_book = UserBook(
        owner_id=owner_id,
        book_id=book_id,
        is_available=is_available,
    )
    session.add(user_book)
    await session.commit()
    return await get_user_book_by_id(session, user_book.id)


async def update_user_book(
    session: AsyncSession,
    user_book: UserBook,
    user_book_data: dict,
) -> UserBook:
    for field, value in user_book_data.items():
        setattr(user_book, field, value)

    await session.commit()
    return await get_user_book_by_id(session, user_book.id)


async def delete_user_book(session: AsyncSession, user_book: UserBook) -> None:
    await session.delete(user_book)
    await session.commit()
