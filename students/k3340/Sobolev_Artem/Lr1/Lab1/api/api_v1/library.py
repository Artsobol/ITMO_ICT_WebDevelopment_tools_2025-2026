from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth import get_current_active_auth_user, get_session
from api.api_v1.schemas import UserBookCreate, UserBookResponse, UserBookUpdate
from api.api_v1.schemas.users import UserSchema
from services.user_book import (
    UserBookBookNotFoundError,
    UserBookConflictError,
    UserBookForbiddenError,
    UserBookNotFoundError,
    add_book_to_library,
    get_user_book_or_raise,
    remove_library_item,
    search_library,
    update_library_item,
)

router = APIRouter(prefix="/library", tags=["Библиотека"])


@router.get("/", response_model=list[UserBookResponse], summary="Искать книги в библиотеке")
async def search_library_endpoint(
    search_query: str | None = Query(
        default=None,
        alias="поиск",
        min_length=1,
        max_length=255,
        title="Поиск",
        description="Поиск по названию книги, описанию, автору и владельцу",
    ),
    q: str | None = Query(default=None, min_length=1, max_length=255, include_in_schema=False),
    genre_filter: int | None = Query(
        default=None,
        alias="идентификатор_жанра",
        title="Идентификатор жанра",
        description="Фильтр по жанру книги.",
    ),
    genre_id: int | None = Query(default=None, include_in_schema=False),
    owner_filter: int | None = Query(
        default=None,
        alias="идентификатор_владельца",
        title="Идентификатор владельца",
        description="Показать книги конкретного владельца",
    ),
    owner_id: int | None = Query(default=None, include_in_schema=False),
    available_filter: bool | None = Query(
        default=None,
        alias="только_доступные",
        title="Только доступные",
        description="Показывать только книги, доступные для обмена",
    ),
    available_only: bool | None = Query(default=None, include_in_schema=False),
    exclude_own: bool | None = Query(
        default=None,
        alias="исключить_мои",
        title="Исключить мои книги",
        description="Исключать из поиска книги текущего пользователя",
    ),
    exclude_mine: bool | None = Query(default=None, include_in_schema=False),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    resolved_search = search_query if search_query is not None else q
    resolved_genre_id = genre_filter if genre_filter is not None else genre_id
    resolved_owner_id = owner_filter if owner_filter is not None else owner_id
    resolved_available_only = (
        available_filter if available_filter is not None else available_only
    )
    if resolved_available_only is None:
        resolved_available_only = True
    resolved_exclude_mine = exclude_own if exclude_own is not None else exclude_mine
    if resolved_exclude_mine is None:
        resolved_exclude_mine = True

    return await search_library(
        session,
        search=resolved_search,
        genre_id=resolved_genre_id,
        owner_id=resolved_owner_id,
        exclude_owner_id=user.id if resolved_exclude_mine else None,
        available_only=resolved_available_only,
    )


@router.get("/me", response_model=list[UserBookResponse], summary="Получить мою библиотеку")
async def get_my_library(
    available_filter: bool | None = Query(
        default=None,
        alias="только_доступные",
        title="Только доступные",
        description="Если указано, фильтрует книги по доступности для обмена",
    ),
    available_only: bool | None = Query(default=None, include_in_schema=False),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    resolved_available_only = (
        available_filter if available_filter is not None else available_only
    )
    return await search_library(
        session,
        owner_id=user.id,
        available_only=resolved_available_only,
    )


@router.get("/{user_book_id:int}", response_model=UserBookResponse, summary="Получить элемент библиотеки")
async def get_library_item(
    user_book_id: int = Path(..., title="Идентификатор записи библиотеки", description="Числовой идентификатор записи в библиотеке."),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        return await get_user_book_or_raise(session, user_book_id)
    except UserBookNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/",
    response_model=UserBookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить книгу в мою библиотеку",
)
async def add_book_to_my_library(
    user_book_in: UserBookCreate = Body(
        ...,
        title="Данные записи библиотеки",
        description="Идентификатор книги и признак доступности для обмена",
    ),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        return await add_book_to_library(
            session,
            owner_id=user.id,
            book_id=user_book_in.book_id,
            is_available=user_book_in.is_available,
        )
    except UserBookBookNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UserBookConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This book is already in the user's library",
        ) from exc


@router.patch("/{user_book_id:int}", response_model=UserBookResponse, summary="Обновить запись в моей библиотеке")
async def update_my_library_item(
    user_book_id: int = Path(..., title="Идентификатор записи библиотеки", description="Числовой идентификатор записи в библиотеке"),
    user_book_in: UserBookUpdate = Body(
        ...,
        title="Изменения записи библиотеки",
        description="Поля записи библиотеки, которые нужно обновить",
    ),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        return await update_library_item(
            session,
            user_book_id=user_book_id,
            owner_id=user.id,
            user_book_data=user_book_in.model_dump(),
        )
    except UserBookNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UserBookForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.delete("/{user_book_id:int}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить запись из моей библиотеки")
async def delete_my_library_item(
    user_book_id: int = Path(..., title="Идентификатор записи библиотеки", description="Числовой идентификатор записи в библиотеке"),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        await remove_library_item(
            session,
            user_book_id=user_book_id,
            owner_id=user.id,
        )
    except UserBookNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UserBookForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
