from typing import Annotated, Literal

from pydantic import EmailStr, Field, StringConstraints

from api.api_v1.schemas.base import Base

UserRole = Literal["user", "admin"]

ShortTextStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]
LongTextStr = Annotated[str, StringConstraints(min_length=1, max_length=4000)]


class ProfileFieldsMixin(Base):
    full_name: ShortTextStr | None = Field(default=None, title="Полное имя", description="Полное имя пользователя.")
    bio: LongTextStr | None = Field(default=None, title="О себе", description="Краткая информация о пользователе.")
    skills: LongTextStr | None = Field(default=None, title="Навыки", description="Навыки пользователя.")
    work_experience: LongTextStr | None = Field(default=None, title="Опыт работы", description="Опыт работы пользователя.")
    project_preferences: LongTextStr | None = Field(default=None, title="Предпочтения по проектам", description="Предпочтения пользователя по проектам.")


class ProfileSchema(ProfileFieldsMixin):
    id: int
    user_id: int


class ProfileResponseSchema(ProfileFieldsMixin):
    id: int
    user_id: int


class ProfileSummarySchema(Base):
    full_name: ShortTextStr | None = None


class ProfileUpdateSchema(Base):
    full_name: ShortTextStr | None = None
    bio: LongTextStr | None = None
    skills: LongTextStr | None = None
    work_experience: LongTextStr | None = None
    project_preferences: LongTextStr | None = None


class UserBaseSchema(Base):
    username: str = Field(title="Имя пользователя", description="Уникальное имя пользователя.")
    email: EmailStr | None = Field(default=None, title="Email", description="Адрес электронной почты пользователя.")
    role: UserRole = Field(default="user", title="Роль", description="Роль пользователя в системе.")
    active: bool = Field(default=True, title="Активен", description="Активна ли учетная запись пользователя.")


class UserSchema(UserBaseSchema):
    id: int
    password: bytes
    profile: ProfileSchema | None = None


class UserCreateSchema(Base):
    username: str = Field(title="Имя пользователя", description="Уникальное имя нового пользователя.")
    password: str = Field(min_length=4, title="Пароль", description="Пароль нового пользователя.")
    email: EmailStr | None = Field(default=None, title="Email", description="Адрес электронной почты нового пользователя.")


class UserLoginSchema(Base):
    username: str = Field(title="Имя пользователя", description="Имя пользователя для входа.")
    password: str = Field(title="Пароль", description="Пароль пользователя для входа.")


class UserResponseSchema(UserBaseSchema):
    id: int
    profile: ProfileResponseSchema | None = None


class UserPublicSchema(Base):
    id: int
    username: str
    role: UserRole = "user"
    profile: ProfileSummarySchema | None = None


class UserSummarySchema(Base):
    id: int
    username: str
    role: UserRole = "user"
    profile: ProfileSummarySchema | None = None


class UserUpdateSchema(Base):
    email: EmailStr | None = Field(default=None, title="Email", description="Новый адрес электронной почты.")


class UserPasswordChangeSchema(Base):
    current_password: str = Field(min_length=4, title="Текущий пароль", description="Текущий пароль пользователя.")
    new_password: str = Field(min_length=4, title="Новый пароль", description="Новый пароль пользователя.")

