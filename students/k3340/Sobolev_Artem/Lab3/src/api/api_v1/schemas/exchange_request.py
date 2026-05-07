from datetime import datetime
from typing import Annotated
from typing import Literal

from pydantic import Field, StringConstraints

from api.api_v1.schemas.base import Base
from api.api_v1.schemas.user_book import UserBookResponse
from api.api_v1.schemas.users import UserSummarySchema

ExchangeRequestStatus = Literal["pending", "accepted", "rejected", "cancelled"]
ExchangeRequestMessageStr = Annotated[
    str,
    StringConstraints(min_length=1, max_length=2000),
]


class ExchangeRequestCreate(Base):
    user_book_id: int = Field(title="Идентификатор записи библиотеки", description="Идентификатор книги пользователя, на которую создаётся заявка.")
    message: ExchangeRequestMessageStr | None = Field(default=None, title="Сообщение", description="Комментарий к заявке на обмен.")


class ExchangeRequestStatusUpdate(Base):
    status: Literal["accepted", "rejected", "cancelled"] = Field(
        title="Статус заявки",
        description="Новый статус заявки: accepted, rejected или cancelled.",
    )


class ExchangeRequestResponse(Base):
    id: int
    status: ExchangeRequestStatus
    message: str | None = None
    created_at: datetime
    updated_at: datetime
    requester: UserSummarySchema
    owner: UserSummarySchema
    user_book: UserBookResponse
