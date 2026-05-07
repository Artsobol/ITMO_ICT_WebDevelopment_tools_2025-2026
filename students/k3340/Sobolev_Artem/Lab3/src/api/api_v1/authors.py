from typing import AsyncGenerator

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth import get_current_admin_auth_user
from api.api_v1.schemas.author import AuthorResponse, AuthorCreate, AuthorUpdate
from api.api_v1.schemas.users import UserSchema
from core.models import db_helper
from services.author import (
    AuthorNotFound,
    AuthorSlugConflictError,
    create_author,
    delete_author,
    get_author_by_id_or_raise,
    get_author_by_slug_or_raise,
    list_authors,
    update_author,
)

router = APIRouter(prefix="/authors", tags=["Авторы"])


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.sessiong_getter():
        yield session


@router.get("/", response_model=list[AuthorResponse], summary="Получить список авторов")
async def get_authors(session: AsyncSession = Depends(get_session)):
    return await list_authors(session)


@router.get("/{author_id:int}", response_model=AuthorResponse, summary="Получить автора по идентификатору")
async def get_author_by_id_endpoint(
    author_id: int = Path(..., title="Идентификатор автора", description="Числовой идентификатор автора."),
    session: AsyncSession = Depends(get_session),
):
    try:
        return await get_author_by_id_or_raise(session, author_id)
    except AuthorNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get("/{slug:str}", response_model=AuthorResponse, summary="Получить автора по slug")
async def get_author_by_slug_endpoint(
    slug: str = Path(..., title="Slug автора", description="Уникальный slug автора."),
    session: AsyncSession = Depends(get_session),
):
    try:
        return await get_author_by_slug_or_raise(session, slug)
    except AuthorNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post(
    "/",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать автора",
)
async def create_author_endpoint(
    author_in: AuthorCreate = Body(
        ...,
        title="Данные автора",
        description="Имя автора и его slug.",
    ),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_admin_auth_user),
):
    try:
        return await create_author(session, author_in.model_dump())
    except AuthorSlugConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Author with this slug already exists",
        ) from exc


@router.patch("/{author_id}", response_model=AuthorResponse, summary="Обновить автора")
async def update_author_endpoint(
    author_id: int = Path(..., title="Идентификатор автора", description="Числовой идентификатор автора."),
    author_in: AuthorUpdate = Body(
        ...,
        title="Изменения автора",
        description="Поля автора, которые нужно обновить.",
    ),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_admin_auth_user),
):
    try:
        return await update_author(
            session, author_id, author_in.model_dump(exclude_unset=True)
        )
    except AuthorNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except AuthorSlugConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Author with this slug already exists",
        ) from exc


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить автора")
async def delete_author_endpoint(
    author_id: int = Path(..., title="Идентификатор автора", description="Числовой идентификатор автора."),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_admin_auth_user),
):
    try:
        await delete_author(session, author_id)
    except AuthorNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
