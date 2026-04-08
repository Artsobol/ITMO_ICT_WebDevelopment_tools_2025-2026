from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth import get_current_active_auth_user, get_session
from api.api_v1.schemas.users import (
    ProfileResponseSchema,
    UserPasswordChangeSchema,
    UserPublicSchema,
    UserResponseSchema,
    UserSchema,
    UserUpdateSchema,
)
from services.user import (
    UserEmailConflictError,
    UserInvalidPasswordError,
    UserNotFoundError,
    UserPasswordConflictError,
    change_user_password,
    get_user_or_raise,
    list_users,
    update_user_account,
)

router = APIRouter(prefix="/users", tags=["Пользователи"])


def to_user_response(user: UserSchema) -> UserResponseSchema:
    return UserResponseSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        active=user.active,
        profile=(
            ProfileResponseSchema.model_validate(user.profile)
            if user.profile is not None
            else None
        ),
    )


@router.get("/", response_model=list[UserPublicSchema], summary="Получить список пользователей")
async def get_users_endpoint(
    search_query: str | None = Query(
        default=None,
        alias="поиск",
        min_length=1,
        max_length=255,
        title="Поиск",
        description="Поиск по имени пользователя и профилю",
    ),
    search: str | None = Query(default=None, min_length=1, max_length=255, include_in_schema=False),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_active_auth_user),
):
    return await list_users(session, search=search_query if search_query is not None else search)


@router.get("/me", response_model=UserResponseSchema, summary="Получить данные текущего пользователя")
def get_my_user(user: UserSchema = Depends(get_current_active_auth_user)):
    return to_user_response(user)


@router.patch("/me", response_model=UserResponseSchema, summary="Обновить аккаунт текущего пользователя")
async def update_my_user(
    user_in: UserUpdateSchema = Body(
        ...,
        title="Изменения аккаунта",
        description="Поля аккаунта, которые нужно обновить.",
    ),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        updated_user = await update_user_account(
            session,
            user.id,
            user_in.model_dump(exclude_unset=True),
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UserEmailConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from exc

    return to_user_response(updated_user)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT, summary="Изменить пароль текущего пользователя")
async def change_my_password(
    password_in: UserPasswordChangeSchema = Body(
        ...,
        title="Данные для смены пароля",
        description="Текущий и новый пароль пользователя.",
    ),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        await change_user_password(
            session,
            user_id=user.id,
            current_password=password_in.current_password,
            new_password=password_in.new_password,
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (UserInvalidPasswordError, UserPasswordConflictError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{user_id:int}", response_model=UserPublicSchema, summary="Получить публичные данные пользователя")
async def get_user_public_data(
    user_id: int = Path(..., title="Идентификатор пользователя", description="Числовой идентификатор пользователя."),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        user = await get_user_or_raise(session, user_id)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return UserPublicSchema.model_validate(user)
