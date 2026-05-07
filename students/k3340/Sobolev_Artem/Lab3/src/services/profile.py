from sqlalchemy.ext.asyncio import AsyncSession

from core.cruds import profile as profile_crud
from core.models.profile import Profile
from services.user import UserNotFoundError, get_user_or_raise


class ProfileNotFoundError(Exception):
    pass


async def get_profile_or_raise(session: AsyncSession, user_id: int) -> Profile:
    user = await get_user_or_raise(session, user_id)
    if user.profile is None:
        raise ProfileNotFoundError(f"Profile for user id={user_id} not found")
    return user.profile


async def update_profile(
    session: AsyncSession,
    user_id: int,
    profile_data: dict,
) -> Profile:
    user = await get_user_or_raise(session, user_id)
    if user.profile is None:
        return await profile_crud.create_profile(session, user_id, profile_data)
    return await profile_crud.update_profile(session, user.profile, profile_data)
