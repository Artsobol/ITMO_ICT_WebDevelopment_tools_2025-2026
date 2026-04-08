from sqlalchemy.orm import Mapped, mapped_column


class VersionMixin:
    version: Mapped[int] = mapped_column(default=0, nullable=False)
