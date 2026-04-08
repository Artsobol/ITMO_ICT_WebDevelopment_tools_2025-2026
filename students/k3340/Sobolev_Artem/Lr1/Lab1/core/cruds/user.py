from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models.profile import Profile
from core.models.user import User


def _user_load_options():
    return (selectinload(User.profile),)


async def get_all_users(
    session: AsyncSession,
    search: str | None = None,
    only_active: bool = True,
) -> list[User]:
    stmt = select(User).options(*_user_load_options())

    if only_active:
        stmt = stmt.where(User.active.is_(True))

    if search:
        pattern = f"%{search}%"
        stmt = stmt.outerjoin(User.profile).where(
            or_(
                User.username.ilike(pattern),
                Profile.full_name.ilike(pattern),
                Profile.skills.ilike(pattern),
                Profile.project_preferences.ilike(pattern),
            )
        )

    stmt = stmt.order_by(User.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    stmt = select(User).options(*_user_load_options()).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).options(*_user_load_options()).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = select(User).options(*_user_load_options()).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username_or_email(
    session: AsyncSession,
    username: str,
    email: str | None,
) -> User | None:
    conditions = [User.username == username]
    if email:
        conditions.append(User.email == email)

    stmt = select(User).options(*_user_load_options()).where(or_(*conditions))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    username: str,
    password_hash: bytes,
    email: str | None = None,
    role: str = "user",
) -> User:
    user = User(
        username=username,
        password=password_hash,
        email=email,
        role=role,
        active=True,
    )
    session.add(user)
    await session.commit()
    return await get_user_by_id(session, user.id)


async def update_user(session: AsyncSession, user: User, user_data: dict) -> User:
    if not user_data:
        return user

    for field, value in user_data.items():
        setattr(user, field, value)

    await session.commit()
    return await get_user_by_id(session, user.id)
