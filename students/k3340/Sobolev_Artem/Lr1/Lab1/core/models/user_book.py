from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.mixins import CreatedAtMixin, IntIdMixin


class UserBook(IntIdMixin, CreatedAtMixin, Base):
    __tablename__ = "user_books"
    __table_args__ = (
        UniqueConstraint("owner_id", "book_id"),
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    owner: Mapped["User"] = relationship(back_populates="library_items")
    book: Mapped["Book"] = relationship(back_populates="user_books")
    exchange_requests: Mapped[list["ExchangeRequest"]] = relationship(
        back_populates="user_book",
        cascade="all, delete-orphan",
    )
