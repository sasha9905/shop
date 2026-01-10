from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.repositories.base_repository import BaseRepository
from src.models import Order, OrderItem


class OrderRepository(BaseRepository):
    """
    Репозиторий для работы с заказами
    """
    async def create_order(self, order: Order) -> Order:
        """
        Создать новый заказ

        Args:
            order: Объект заказа для создания

        Returns:
            Созданный заказ (с ID после flush)
        """
        self.session.add(order)
        await self.session.flush()
        return order

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        Получить заказ по ID
        
        Args:
            order_id: ID заказа
            
        Returns:
            Order или None, если заказ не найден
        """
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def get_order_with_relations(self, order_id: int) -> Optional[Order]:
        """
        Получить заказ с загруженными связями (user, product_items, product)
        
        Args:
            order_id: ID заказа
            
        Returns:
            Order с загруженными связями или None, если заказ не найден
        """
        result = await self.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.user),
                selectinload(Order.product_items).selectinload(OrderItem.product)
            )
        )
        return result.scalar_one_or_none()

    async def get_order_item(self, order_id: int, product_id: int) -> Optional[OrderItem]:
        """
        Найти конкретный товар в заказе
        
        Args:
            order_id: ID заказа
            product_id: ID товара
            
        Returns:
            OrderItem или None, если элемент не найден
        """
        result = await self.session.execute(
            select(OrderItem)
            .join(OrderItem.product)
            .where(
                OrderItem.order_id == order_id,
                OrderItem.product_id == product_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all_with_relations(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Получить все заказы с загруженными связями (user, product_items, product)
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список заказов с загруженными связями
        """
        result = await self.session.execute(
            select(Order)
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(Order.user),
                selectinload(Order.product_items).selectinload(OrderItem.product)
            )
        )
        return list(result.scalars().all())

    async def delete_order(self, order: Order) -> None:
        """
        Удалить заказ

        Args:
            order: Заказа для удаления
        """
        async with self.transaction():
            await self.session.delete(order)

_order_repo = None

def get_order_repo():
    global _order_repo

    if _order_repo is None:
        _order_repo = OrderRepository

    return _order_repo
