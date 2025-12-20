from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing_extensions import Annotated

from src.models.base_classes import Base, IDMixin

client_fk = Annotated[int, mapped_column(ForeignKey('clients.id'))]


class Order(Base, IDMixin):
    __tablename__ = 'orders'

    client_id: Mapped[client_fk]
    total_quantity: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    client: Mapped["Client"] = relationship(back_populates="orders")

    product_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )
