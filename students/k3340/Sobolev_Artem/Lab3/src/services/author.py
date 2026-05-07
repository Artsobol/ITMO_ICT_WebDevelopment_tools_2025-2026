from sqlalchemy.ext.asyncio import AsyncSession

from core.cruds import author as author_crud
from core.models.author import Author


class AuthorNotFound(Exception):
    pass


class AuthorSlugConflictError(Exception):
    pass


async def list_authors(session):
    return await author_crud.get_all_authors(session)


async def get_author_by_id_or_raise(session: AsyncSession, id: int) -> Author:
    author = await author_crud.get_author_by_id(session, id)
    if author is None:
        raise AuthorNotFound(f"Author with id={id} not found")
    return author


async def get_author_by_slug_or_raise(session: AsyncSession, slug: str) -> Author:
    author = await author_crud.get_author_by_slug(session, slug)
    if author is None:
        raise AuthorNotFound(f"Author with slug={slug} not found")
    return author


async def create_author(session: AsyncSession, author_data: dict) -> Author:
    existing = await author_crud.get_author_by_slug(session, author_data["slug"])
    if existing is not None:
        raise AuthorSlugConflictError("Author with this slug already exists")
    return await author_crud.create_author(session, author_data)


async def update_author(
    session: AsyncSession, author_id: int, author_data: dict
) -> Author:
    author = await get_author_by_id_or_raise(session, author_id)

    new_slug = author_data.get("slug")
    if new_slug and new_slug != author.slug:
        existing = await author_crud.get_author_by_slug(session, new_slug)
        if existing is not None and existing.id != author.id:
            raise AuthorSlugConflictError("Author with this slug already exists")

    return await author_crud.update_author(session, author, author_data)


async def delete_author(session: AsyncSession, author_id: int) -> None:
    author = await get_author_by_id_or_raise(session, author_id)
    await author_crud.delete_author(session, author)
