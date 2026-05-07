from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from api.api_v1.schemas.base import Base

NameStr = Annotated[str, StringConstraints(min_length=2, max_length=80)]
SlugStr = Annotated[str, StringConstraints(min_length=2, max_length=80)]


class AuthorBase(Base):
    name: NameStr = Field(title="Имя автора", description="Полное имя автора.")
    slug: SlugStr = Field(title="Slug автора", description="Уникальный slug автора.")


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(Base):
    name: NameStr | None = Field(default=None, title="Имя автора", description="Новое имя автора.")
    slug: SlugStr | None = Field(default=None, title="Slug автора", description="Новый slug автора.")


class AuthorResponse(AuthorBase):
    id: int
    name: NameStr
    slug: SlugStr
    created_at: datetime
    updated_at: datetime
