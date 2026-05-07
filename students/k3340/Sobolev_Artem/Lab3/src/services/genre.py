from sqlalchemy.ext.asyncio import AsyncSession

from core.cruds import genre as genre_crud
from core.models import Genre


class GenreNotFoundError(Exception):
    pass


class GenreSlugConflictError(Exception):
    pass


async def list_genres(session: AsyncSession):
    return await genre_crud.get_all_genres(session)


async def get_genre_or_raise(session: AsyncSession, genre_id: int) -> Genre:
    genre = await genre_crud.get_genre_by_id(session, genre_id)
    if genre is None:
        raise GenreNotFoundError(f"Genre with id={genre_id} not found")
    return genre


async def create_genre(session: AsyncSession, genre_data: dict) -> Genre:
    existing = await genre_crud.get_genre_by_slug(session, genre_data["slug"])
    if existing is not None:
        raise GenreSlugConflictError("Genre with this slug already exists")
    return await genre_crud.create_genre(session, genre_data)


async def update_genre(session: AsyncSession, genre_id: int, genre_data: dict) -> Genre:
    genre = await get_genre_or_raise(session, genre_id)

    new_slug = genre_data.get("slug")
    if new_slug and new_slug != genre.slug:
        existing = await genre_crud.get_genre_by_slug(session, new_slug)
        if existing is not None and existing.id != genre.id:
            raise GenreSlugConflictError("Genre with this slug already exists")

    return await genre_crud.update_genre(session, genre, genre_data)


async def delete_genre(session: AsyncSession, genre_id: int) -> None:
    genre = await get_genre_or_raise(session, genre_id)
    await genre_crud.delete_genre(session, genre)
