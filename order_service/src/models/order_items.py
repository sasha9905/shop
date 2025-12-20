from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing_extensions import Annotated

from src.base_models.base_classes import Base, IDMixin

order_fk = Annotated[int, mapped_column(ForeignKey('orders.id', ondelete='CASCADE'))]
product_fk = Annotated[int, mapped_column(ForeignKey('products.id', ondelete='CASCADE'))]


class OrderItem(Base, IDMixin):
    __tablename__ = 'order_items'
    __table_args__ = (
        UniqueConstraint('order_id', 'product_id', name='uq_order_product'),
    )

    order_id: Mapped[order_fk]
    product_id: Mapped[product_fk]
    product_quantity: Mapped[int]

    order: Mapped["Order"] = relationship(back_populates="product_items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
