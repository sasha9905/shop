from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing_extensions import Annotated

from src.models.base_classes import Base, IDMixin, NameMixin


class Product(Base, IDMixin, NameMixin):
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint('storage_quantity >= 0', name='check_quantity_positive'),
        CheckConstraint('price >= 0', name='check_price_positive'),
    )

    storage_quantity: Mapped[int]
    price: Mapped[int]

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product"
    )
