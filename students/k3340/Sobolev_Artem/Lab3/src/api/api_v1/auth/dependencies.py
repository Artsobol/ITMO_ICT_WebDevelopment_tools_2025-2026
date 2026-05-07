from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TOKEN_TYPE_FIELD
from api.api_v1.auth.service import to_user_schema
from api.api_v1.schemas.users import UserSchema
from auth.utils import decode_jwt
from core.cruds.user import get_user_by_username
from core.models import db_helper

bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    bearerFormat="JWT",
    description="Вставьте access token для защищенных эндпоинтов.",
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.sessiong_getter():
        yield session


def get_token_payload_by_token(token: str) -> dict:
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc
    return payload


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    return get_token_payload_by_token(credentials.credentials)


def _validate_token_type(payload: dict, expected_type: str) -> None:
    token_type = payload.get(TOKEN_TYPE_FIELD)
    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type {token_type!r}, expected {expected_type!r}",
        )


async def _get_user_by_token_sub(payload: dict, session: AsyncSession) -> UserSchema:
    username: str | None = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await get_user_by_username(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return to_user_schema(user)


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(get_session),
) -> UserSchema:
    _validate_token_type(payload, ACCESS_TOKEN_TYPE)
    return await _get_user_by_token_sub(payload, session)


async def get_current_auth_user_for_refresh(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(get_session),
) -> UserSchema:
    _validate_token_type(payload, REFRESH_TOKEN_TYPE)
    return await _get_user_by_token_sub(payload, session)


async def get_auth_user_by_refresh_token(
    refresh_token: str,
    session: AsyncSession,
) -> UserSchema:
    payload = get_token_payload_by_token(refresh_token)
    _validate_token_type(payload, REFRESH_TOKEN_TYPE)
    return await _get_user_by_token_sub(payload, session)


def get_current_active_auth_user(user: UserSchema = Depends(get_current_auth_user)) -> UserSchema:
    if user.active:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")


def get_current_admin_auth_user(
    user: UserSchema = Depends(get_current_active_auth_user),
) -> UserSchema:
    if user.role == "admin":
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required",
    )
