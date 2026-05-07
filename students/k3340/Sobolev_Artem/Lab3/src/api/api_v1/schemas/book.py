from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from api.api_v1.schemas.base import Base
from api.api_v1.schemas.genre import GenreResponse
from api.api_v1.schemas.author import AuthorResponse

BookTitleStr = Annotated[str, StringConstraints(min_length=2, max_length=128)]
BookDescriptionStr = Annotated[str, StringConstraints(min_length=1, max_length=2048)]


class BookBase(Base):
    title: BookTitleStr = Field(title="Название книги", description="Название книги.")
    description: BookDescriptionStr | None = Field(default=None, title="Описание книги", description="Краткое описание книги.")
    genre_id: int | None = Field(default=None, title="Идентификатор жанра", description="Идентификатор жанра книги. Поле необязательное.")


class BookCreate(BookBase):
    author_ids: list[int] = Field(
        default_factory=list,
        title="Идентификаторы авторов",
        description="Список идентификаторов авторов книги. Поле необязательное.",
    )


class BookUpdate(Base):
    title: BookTitleStr | None = Field(default=None, title="Название книги", description="Новое название книги.")
    description: BookDescriptionStr | None = Field(default=None, title="Описание книги", description="Новое описание книги.")
    genre_id: int | None = Field(default=None, title="Идентификатор жанра", description="Новый идентификатор жанра книги.")
    author_ids: list[int] | None = Field(default=None, title="Идентификаторы авторов", description="Новый список идентификаторов авторов.")


class BookResponse(Base):
    id: int
    title: BookTitleStr
    description: BookDescriptionStr | None = None
    genre: GenreResponse | None = None
    authors: list[AuthorResponse]
    created_at: datetime
    updated_at: datetime
