import enum

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from src.models.base_classes import Base, UUIDMixin, NameMixin


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base, UUIDMixin, NameMixin):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
