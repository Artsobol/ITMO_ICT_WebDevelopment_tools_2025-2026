from pydantic import BaseModel, Field

from api.api_v1.schemas.users import UserResponseSchema


class TokenInfo(BaseModel):
    access_token: str = Field(title="Access token", description="JWT access token.")
    refresh_token: str | None = Field(default=None, title="Refresh token", description="JWT refresh token.")
    token_type: str = Field(default="bearer", title="Тип токена", description="Тип авторизации.")


class AuthTokenInfo(TokenInfo):
    user: UserResponseSchema = Field(title="Пользователь", description="Данные авторизованного пользователя.")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1,
        title="Refresh token",
        description="Refresh token для получения нового access token.",
    )
