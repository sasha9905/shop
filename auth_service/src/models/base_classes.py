import uuid

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    """Миксин с UUID ID"""
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class NameMixin:
    username: Mapped[str]
