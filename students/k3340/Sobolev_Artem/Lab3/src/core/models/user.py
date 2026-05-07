from enum import StrEnum

from sqlalchemy import Boolean, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.mixins import CreatedAtMixin, IntIdMixin, UpdatedAtMixin


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class User(IntIdMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    role: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=UserRole.USER.value,
        server_default=UserRole.USER.value,
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    profile: Mapped["Profile | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    library_items: Mapped[list["UserBook"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    sent_exchange_requests: Mapped[list["ExchangeRequest"]] = relationship(
        back_populates="requester",
        foreign_keys="ExchangeRequest.requester_id",
        cascade="all, delete-orphan",
    )
    received_exchange_requests: Mapped[list["ExchangeRequest"]] = relationship(
        back_populates="owner",
        foreign_keys="ExchangeRequest.owner_id",
        cascade="all, delete-orphan",
    )
