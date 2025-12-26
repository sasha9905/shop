import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing_extensions import Annotated

from src.models.base_classes import Base, IDMixin

client_fk = Annotated[uuid.UUID, mapped_column(ForeignKey('users.id'))]


class Order(Base, IDMixin):
    __tablename__ = 'orders'

    user_id: Mapped[client_fk]
    total_quantity: Mapped[int]

    user: Mapped["User"] = relationship(back_populates="orders")

    product_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )
