from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth.dependencies import (
    get_auth_user_by_refresh_token,
    get_current_active_auth_user,
    get_session,
)
from api.api_v1.auth.service import authenticate_user, register_user
from api.api_v1.auth.tokens import create_access_token, create_refresh_token
from api.api_v1.schemas.token import AuthTokenInfo, RefreshTokenRequest, TokenInfo
from api.api_v1.schemas.users import (
    ProfileResponseSchema,
    UserCreateSchema,
    UserLoginSchema,
    UserResponseSchema,
    UserSchema,
)

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


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


def build_token_info(user: UserSchema) -> TokenInfo:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/register",
    response_model=AuthTokenInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register_new_user(
    user_in: UserCreateSchema = Body(
        ...,
        title="Данные регистрации",
        description="Логин, пароль и email нового пользователя.",
    ),
    session: AsyncSession = Depends(get_session),
):
    user = await register_user(
        session=session,
        username=user_in.username,
        password=user_in.password,
        email=user_in.email,
    )
    token_info = build_token_info(user)
    return AuthTokenInfo(
        access_token=token_info.access_token,
        refresh_token=token_info.refresh_token,
        user=to_user_response(user),
    )


@router.post(
    "/login",
    response_model=AuthTokenInfo,
    summary="Вход пользователя",
)
async def auth_user_issue_jwt(
    user_in: UserLoginSchema = Body(
        ...,
        title="Данные для входа",
        description="Логин и пароль пользователя.",
    ),
    session: AsyncSession = Depends(get_session),
):
    user = await authenticate_user(session, user_in.username, user_in.password)
    token_info = build_token_info(user)
    return AuthTokenInfo(
        access_token=token_info.access_token,
        refresh_token=token_info.refresh_token,
        user=to_user_response(user),
    )


@router.get(
    "/users/me",
    response_model=UserResponseSchema,
    summary="Получить данные текущего пользователя",
)
def auth_user_check_self_info(user: UserSchema = Depends(get_current_active_auth_user)):
    return to_user_response(user)


@router.post(
    "/refresh",
    response_model=TokenInfo,
    response_model_exclude_none=True,
    summary="Обновить access token",
)
async def auth_refresh_jwt(
    token_in: RefreshTokenRequest = Body(
        ...,
        title="Refresh token",
        description="Тело запроса с refresh token для получения нового access token.",
    ),
    session: AsyncSession = Depends(get_session),
):
    user = await get_auth_user_by_refresh_token(token_in.refresh_token, session)
    access_token = create_access_token(user)
    return TokenInfo(access_token=access_token)
