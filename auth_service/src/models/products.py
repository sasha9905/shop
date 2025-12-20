from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing_extensions import Annotated

from src.models.base_classes import Base, IDMixin, NameMixin

category_fk = Annotated[int, mapped_column(ForeignKey('categories.id'))]


class Product(Base, IDMixin, NameMixin):
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint('storage_quantity >= 0', name='check_quantity_positive'),
        CheckConstraint('price >= 0', name='check_price_positive'),
    )

    storage_quantity: Mapped[int]
    price: Mapped[int]
    category_id: Mapped[category_fk]

    category: Mapped["Category"] = relationship(back_populates="products")

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product"
    )
