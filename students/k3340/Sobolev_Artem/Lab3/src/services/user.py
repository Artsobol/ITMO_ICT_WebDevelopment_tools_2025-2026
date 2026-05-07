from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import hash_password, validate_password
from core.cruds import user as user_crud
from core.models.user import User


class UserNotFoundError(Exception):
    pass


class UserEmailConflictError(Exception):
    pass


class UserInvalidPasswordError(Exception):
    pass


class UserPasswordConflictError(Exception):
    pass


async def list_users(session: AsyncSession, search: str | None = None) -> list[User]:
    return await user_crud.get_all_users(session, search=search, only_active=True)


async def get_user_or_raise(session: AsyncSession, user_id: int) -> User:
    user = await user_crud.get_user_by_id(session, user_id)
    if user is None or not user.active:
        raise UserNotFoundError(f"User with id={user_id} not found")
    return user


async def update_user_account(
    session: AsyncSession,
    user_id: int,
    user_data: dict,
) -> User:
    user = await get_user_or_raise(session, user_id)

    new_email = user_data.get("email")
    if new_email and new_email != user.email:
        existing = await user_crud.get_user_by_email(session, new_email)
        if existing is not None and existing.id != user.id:
            raise UserEmailConflictError("User with this email already exists")

    return await user_crud.update_user(session, user, user_data)


async def change_user_password(
    session: AsyncSession,
    *,
    user_id: int,
    current_password: str,
    new_password: str,
) -> User:
    user = await get_user_or_raise(session, user_id)

    if not validate_password(current_password, user.password):
        raise UserInvalidPasswordError("Current password is incorrect")

    if validate_password(new_password, user.password):
        raise UserPasswordConflictError(
            "New password must be different from current password"
        )

    return await user_crud.update_user(
        session,
        user,
        {"password": hash_password(new_password)},
    )
