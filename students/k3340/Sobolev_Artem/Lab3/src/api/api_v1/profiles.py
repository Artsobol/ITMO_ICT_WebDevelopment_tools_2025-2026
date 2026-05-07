from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth import get_current_active_auth_user, get_session
from api.api_v1.schemas.users import (
    ProfileResponseSchema,
    ProfileUpdateSchema,
    UserSchema,
)
from services.profile import ProfileNotFoundError, get_profile_or_raise, update_profile
from services.user import UserNotFoundError

router = APIRouter(prefix="/profiles", tags=["Профили"])


@router.get("/me", response_model=ProfileResponseSchema, summary="Получить мой профиль")
async def get_my_profile(
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        profile = await get_profile_or_raise(session, user.id)
    except (UserNotFoundError, ProfileNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ProfileResponseSchema.model_validate(profile)


@router.patch("/me", response_model=ProfileResponseSchema, summary="Обновить мой профиль")
async def update_my_profile(
    profile_in: ProfileUpdateSchema = Body(
        ...,
        title="Изменения профиля",
        description="Поля профиля, которые нужно обновить.",
    ),
    session: AsyncSession = Depends(get_session),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        profile = await update_profile(
            session,
            user.id,
            profile_in.model_dump(exclude_unset=True),
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ProfileResponseSchema.model_validate(profile)


@router.get("/{user_id:int}", response_model=ProfileResponseSchema, summary="Получить профиль пользователя")
async def get_user_profile(
    user_id: int = Path(..., title="Идентификатор пользователя", description="Числовой идентификатор пользователя."),
    session: AsyncSession = Depends(get_session),
    _user: UserSchema = Depends(get_current_active_auth_user),
):
    try:
        profile = await get_profile_or_raise(session, user_id)
    except (UserNotFoundError, ProfileNotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ProfileResponseSchema.model_validate(profile)
