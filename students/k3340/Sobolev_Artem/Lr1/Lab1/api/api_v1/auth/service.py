from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.schemas.users import UserSchema
from auth.utils import hash_password, validate_password
from core.cruds.user import create_user, get_user_by_username, get_user_by_username_or_email
from core.models.user import User, UserRole


def to_user_schema(user: User) -> UserSchema:
    return UserSchema.model_validate(user)


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> UserSchema:
    unauthorized_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )

    user = await get_user_by_username(session, username)
    if not user:
        raise unauthorized_exc

    if not validate_password(password=password, hashed_pwd=user.password):
        raise unauthorized_exc

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive",
        )
    return to_user_schema(user)


async def register_user(
    session: AsyncSession,
    username: str,
    password: str,
    email: str | None = None,
) -> UserSchema:
    existing_user = await get_user_by_username_or_email(session, username, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    user = await create_user(
        session,
        username,
        hash_password(password),
        email=email,
        role=UserRole.USER.value,
    )
    return to_user_schema(user)
