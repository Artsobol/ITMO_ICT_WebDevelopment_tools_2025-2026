from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Genre


async def get_all_genres(session: AsyncSession) -> Sequence[Genre]:
    stmt = select(Genre).order_by(Genre.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_genre_by_id(session: AsyncSession, genre_id: int) -> Genre | None:
    return await session.get(Genre, genre_id)


async def get_genre_by_slug(session: AsyncSession, slug: str) -> Genre | None:
    stmt = select(Genre).where(Genre.slug == slug)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_genre(session: AsyncSession, genre_data: dict) -> Genre:
    genre_obj = Genre(**genre_data)
    session.add(genre_obj)
    await session.commit()
    await session.refresh(genre_obj)
    return genre_obj


async def update_genre(
    session: AsyncSession,
    genre: Genre,
    genre_data: dict,
) -> Genre:
    if not genre_data:
        return genre

    for field, value in genre_data.items():
        setattr(genre, field, value)

    await session.commit()
    await session.refresh(genre)
    return genre


async def delete_genre(session: AsyncSession, genre: Genre) -> None:
    await session.delete(genre)
    await session.commit()
