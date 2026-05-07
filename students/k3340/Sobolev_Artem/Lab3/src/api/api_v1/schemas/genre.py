from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from api.api_v1.schemas.base import Base

SlugStr = Annotated[str, StringConstraints(min_length=2, max_length=128)]
TitleStr = Annotated[str, StringConstraints(min_length=2, max_length=64)]
DescriptionStr = Annotated[str, StringConstraints(min_length=1, max_length=1024)]


class GenreBase(Base):
    title: TitleStr = Field(title="Название жанра", description="Название жанра книги.")
    description: DescriptionStr | None = Field(default=None, title="Описание жанра", description="Краткое описание жанра.")
    slug: SlugStr = Field(title="Slug жанра", description="Уникальный slug жанра.")


class GenreCreate(GenreBase):
    pass


class GenreUpdate(Base):
    title: TitleStr | None = Field(default=None, title="Название жанра", description="Новое название жанра.")
    description: DescriptionStr | None = Field(default=None, title="Описание жанра", description="Новое описание жанра.")
    slug: SlugStr | None = Field(default=None, title="Slug жанра", description="Новый slug жанра.")


class GenreResponse(Base):
    id: int
    title: TitleStr
    description: DescriptionStr | None = None
    slug: SlugStr
    created_at: datetime
    updated_at: datetime
    version: int
