from api.api_v1.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TOKEN_TYPE_FIELD
from api.api_v1.schemas.users import UserSchema
from auth.utils import encode_jwt
from core.config import settings


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(payload=jwt_payload, expire_minutes=expire_minutes)


def create_access_token(user: UserSchema) -> str:
    jwt_payload = {
        "id": user.id,
        "sub": user.username,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user: UserSchema) -> str:
    jwt_payload = {"sub": user.username}
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.refresh_token_expire_minutes,
    )
