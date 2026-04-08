from uuid import UUID

from sqlalchemy import String, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core.models.base import Base
from core.models.mixins import CreatedAtMixin, UpdatedAtMixin, IntIdMixin, VersionMixin


class Genre(IntIdMixin, CreatedAtMixin, UpdatedAtMixin, VersionMixin, Base):
    __tablename__ = "genres"

    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    created_by: Mapped[UUID | None] = mapped_column(nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(nullable=True)
    books: Mapped[list["Book"]] = relationship(back_populates="genre")
