from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Genre, Author
from core.models.base import Base
from core.models.mixins import CreatedAtMixin, IntIdMixin, UpdatedAtMixin


class Book(IntIdMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "books"

    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre_id: Mapped[int | None] = mapped_column(ForeignKey("genres.id"), nullable=True)
    genre: Mapped["Genre | None"] = relationship(back_populates="books")
    authors: Mapped[list["Author"]] = relationship(
        secondary="book_authors",
        back_populates="books",
    )
    user_books: Mapped[list["UserBook"]] = relationship(back_populates="book")
