from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.mixins import CreatedAtMixin, IntIdMixin, UpdatedAtMixin


class ExchangeRequest(IntIdMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "exchange_requests"

    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user_book_id: Mapped[int] = mapped_column(ForeignKey("user_books.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending", server_default="pending")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    requester: Mapped["User"] = relationship(
        back_populates="sent_exchange_requests",
        foreign_keys=[requester_id],
    )
    owner: Mapped["User"] = relationship(
        back_populates="received_exchange_requests",
        foreign_keys=[owner_id],
    )
    user_book: Mapped["UserBook"] = relationship(back_populates="exchange_requests")
