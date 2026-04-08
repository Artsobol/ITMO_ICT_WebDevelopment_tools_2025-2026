from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.profile import Profile


async def get_profile_by_user_id(
    session: AsyncSession,
    user_id: int,
) -> Profile | None:
    stmt = select(Profile).where(Profile.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_profile(
    session: AsyncSession,
    user_id: int,
    profile_data: dict,
) -> Profile:
    profile = Profile(user_id=user_id, **profile_data)
    session.add(profile)
    await session.commit()
    return await get_profile_by_user_id(session, user_id)


async def update_profile(
    session: AsyncSession,
    profile: Profile,
    profile_data: dict,
) -> Profile:
    if not profile_data:
        return profile

    for field, value in profile_data.items():
        setattr(profile, field, value)

    await session.commit()
    return await get_profile_by_user_id(session, profile.user_id)
