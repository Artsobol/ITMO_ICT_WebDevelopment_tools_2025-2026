from typing import AsyncGenerator

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth import get_current_active_auth_user, get_current_admin_auth_user
from api.api_v1.schemas import BookCreate, BookResponse, BookUpdate
from api.api_v1.schemas.users import UserSchema
from core.models import db_helper
from services.book import (
    BookAuthorsNotFoundError,
    BookGenreNotFoundError,
    BookNotFoundError,
    create_book_for_owner,
    delete_book,
    get_book_or_raise,
    list_books,
    update_book,
)

router = APIRouter(prefix="/books", tags=["Книги"])


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.sessiong_getter():
        yield session


@router.get("/", response_model=list[BookResponse], summary="Получить список книг")
async def get_books(session: AsyncSession = Depends(get_session)):
    return await list_books(session)


@router.get("/{book_id:int}", response_model=BookResponse, summary="Получить книгу по идентификатору")
async def get_book_by_id_endpoint(
    book_id: int = Path(..., title="Идентификатор книги", description="Числовой идентификатор книги."),
    session: AsyncSession = Depends(get_session),
):
    try:
        return await get_book_or_raise(session, book_id)
    except BookNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать книгу",
)
async def create_book_endpoint(
    book_in: BookCreate = Body(
        ...,
        title="Данные книги",
        description="Название, описание, жанр и список авторов книги.",
    ),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        return await create_book_for_owner(
            session,
            owner_id=user.id,
            book_data=book_in.model_dump(),
        )
    except (BookGenreNotFoundError, BookAuthorsNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book data conflicts with database constraints",
        ) from exc


@router.patch("/{book_id}", response_model=BookResponse, summary="Обновить книгу")
async def update_book_endpoint(
    book_id: int = Path(..., title="Идентификатор книги", description="Числовой идентификатор книги."),
    book_in: BookUpdate = Body(
        ...,
        title="Изменения книги",
        description="Поля книги, которые нужно обновить.",
    ),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_admin_auth_user),
):
    try:
        return await update_book(
            session, book_id, book_in.model_dump(exclude_unset=True)
        )
    except BookNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except (BookGenreNotFoundError, BookAuthorsNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book data conflicts with database constraints",
        ) from exc


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить книгу")
async def delete_book_endpoint(
    book_id: int = Path(..., title="Идентификатор книги", description="Числовой идентификатор книги."),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_admin_auth_user),
):
    try:
        await delete_book(session, book_id)
    except BookNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
