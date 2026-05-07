from datetime import datetime

from pydantic import Field

from api.api_v1.schemas.base import Base
from api.api_v1.schemas.book import BookResponse
from api.api_v1.schemas.users import UserSummarySchema


class UserBookCreate(Base):
    book_id: int = Field(title="Идентификатор книги", description="Идентификатор книги, которую нужно добавить в библиотеку.")
    is_available: bool = Field(default=True, title="Доступна для обмена", description="Доступна ли книга для обмена.")


class UserBookUpdate(Base):
    is_available: bool = Field(title="Доступна для обмена", description="Новое состояние доступности книги для обмена.")


class UserBookResponse(Base):
    id: int
    is_available: bool
    created_at: datetime
    owner: UserSummarySchema
    book: BookResponse
