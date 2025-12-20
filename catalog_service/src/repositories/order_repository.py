from typing import Optional

from sqlalchemy import select

from src.repositories.base_repository import BaseRepository
from src.models import Order, OrderItem


class OrderRepository(BaseRepository):
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def get_order_item(self, order_id: int, product_id: int) -> Optional[OrderItem]:
        """Найти конкретный товар в заказе"""
        result = await self.session.execute(
            select(OrderItem)
            .join(OrderItem.product)
            .where(
                OrderItem.order_id == order_id,
                OrderItem.product_id == product_id
            )
        )
        return result.scalar_one_or_none()
