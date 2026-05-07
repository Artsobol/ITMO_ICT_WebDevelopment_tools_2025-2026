from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.mixins import IntIdMixin, CreatedAtMixin, UpdatedAtMixin


class Author(IntIdMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    books: Mapped[list["Book"]] = relationship(
        secondary="book_authors",
        back_populates="authors",
    )
