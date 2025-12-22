from typing import Optional

from sqlalchemy.orm import Mapped, relationship

from src.models.base_classes import Base, UUIDMixin


class User(Base, UUIDMixin):
    __tablename__ = 'users'

    username: Mapped[str]
    orders: Mapped[Optional[list["Order"]]] = relationship(back_populates="user")
