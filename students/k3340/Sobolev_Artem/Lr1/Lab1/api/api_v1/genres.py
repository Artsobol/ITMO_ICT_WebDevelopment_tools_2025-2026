from typing import AsyncGenerator

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth import get_current_admin_auth_user
from api.api_v1.schemas import GenreCreate, GenreResponse, GenreUpdate
from api.api_v1.schemas.users import UserSchema
from core.models import db_helper
from services.genre import (
    GenreNotFoundError,
    GenreSlugConflictError,
    create_genre,
    delete_genre,
    get_genre_or_raise,
    list_genres,
    update_genre,
)

router = APIRouter(prefix="/genres", tags=["Жанры"])


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.sessiong_getter():
        yield session


@router.get("/", response_model=list[GenreResponse], summary="Получить список жанров")
async def get_genres(session: AsyncSession = Depends(get_session)):
    return await list_genres(session)


@router.get("/{genre_id}", response_model=GenreResponse, summary="Получить жанр по идентификатору")
async def get_genre(
    genre_id: int = Path(..., title="Идентификатор жанра", description="Числовой идентификатор жанра"),
    session: AsyncSession = Depends(get_session),
):
    try:
        return await get_genre_or_raise(session, genre_id)
    except GenreNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/",
    response_model=GenreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать жанр",
)
async def create_genre_endpoint(
    genre_in: GenreCreate = Body(
        ...,
        title="Данные жанра",
        description="Название, описание и slug жанра.",
    ),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_admin_auth_user),
):
    try:
        return await create_genre(session, genre_in.model_dump())
    except GenreSlugConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Genre with this slug already exists",
        ) from exc


@router.patch("/{genre_id}", response_model=GenreResponse, summary="Обновить жанр")
async def update_genre_endpoint(
    genre_id: int = Path(..., title="Идентификатор жанра", description="Числовой идентификатор жанра"),
    genre_in: GenreUpdate = Body(
        ...,
        title="Изменения жанра",
        description="Поля жанра, которые нужно обновить.",
    ),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_admin_auth_user),
):
    try:
        return await update_genre(session, genre_id, genre_in.model_dump(exclude_unset=True))
    except GenreNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except GenreSlugConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Genre with this slug already exists",
        ) from exc


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить жанр")
async def delete_genre_endpoint(
    genre_id: int = Path(..., title="Идентификатор жанра", description="Числовой идентификатор жанра"),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_admin_auth_user),
):
    try:
        await delete_genre(session, genre_id)
    except GenreNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
