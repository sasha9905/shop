import enum

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from src.models.base_classes import Base, UUIDMixin


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base, UUIDMixin):
    __tablename__ = 'users'

    username: Mapped[str]
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
