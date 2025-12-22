import uuid

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass

class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class IDMixin:
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)


class NameMixin:
    name: Mapped[str]
