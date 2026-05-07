from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.author import Author


async def get_all_authors(session: AsyncSession) -> Sequence[Author]:
    stmt = select(Author).order_by(Author.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_author_by_id(session: AsyncSession, author_id: int) -> Author | None:
    return await session.get(Author, author_id)


async def get_author_by_slug(session: AsyncSession, slug: str) -> Author | None:
    stmt = select(Author).where(Author.slug == slug)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_author(session: AsyncSession, author_data: dict) -> Author:
    author_obj = Author(**author_data)
    session.add(author_obj)
    await session.commit()
    await session.refresh(author_obj)
    return author_obj


async def update_author(
    session: AsyncSession, author: Author, author_data: dict
) -> Author:
    if not author_data:
        return author

    for field, value in author_data.items():
        setattr(author, field, value)

    await session.commit()
    await session.refresh(author)
    return author


async def delete_author(session: AsyncSession, author: Author) -> None:
    await session.delete(author)
    await session.commit()
