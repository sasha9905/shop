from typing import List

from src.repositories import OrderRepository
from src.repositories import ProductRepository
from src.models import OrderItem, Order
from src.exceptions import (
    NotFoundError, 
    InsufficientStockError, 
    BusinessRuleError
)
from src.schemas import UpdateOrderDTO, OrderAddDTO


class OrderService:
    """
    Сервис для работы с заказами
    """
    
    def __init__(self, order_repository: OrderRepository,
                 product_repository: ProductRepository):
        """
        Инициализация сервиса
        
        Args:
            order_repository: Репозиторий для работы с заказами
            product_repository: Репозиторий для работы с товарами
        """
        self.order_repo = order_repository
        self.product_repo = product_repository

    async def create_order(self, data: OrderAddDTO) -> Order:
        """
        Создать новый заказ

        Args:
            data: Данные для создания заказа

        Returns:
            Созданный заказ с загруженными связями

        Raises:
            NotFoundError: Если товар не найден
            InsufficientStockError: Если недостаточно товара на складе
        """
        # Оптимизация: получаем все товары одним запросом
        product_ids = [item.product_id for item in data.items]
        products_list = await self.product_repo.get_by_ids(product_ids)

        # Создаем словарь для быстрого доступа
        products_dict = {p.id: p for p in products_list}

        # Проверяем наличие всех товаров и валидируем их доступность
        products = []
        for item_data in data.items:
            product = products_dict.get(item_data.product_id)
            if not product:
                raise NotFoundError(f"Product with id {item_data.product_id} not found")

            # Используем общую валидацию
            self._validate_order_update(product, item_data.quantity)

            products.append((product, item_data))

        # Создаем заказ
        order = Order(
            user_id=data.user_id,
            total_quantity=0
        )
        order = await self.order_repo.create_order(order)

        # Создаем элементы заказа и обновляем остатки на складе
        order_items = []
        entities_to_save = [order]

        for product, item_data in zip(products, data.items):
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                product_quantity=0  # Будет установлено в _apply_order_changes
            )
            order_items.append(order_item)
            entities_to_save.append(order_item)

            self._apply_order_changes(order_item, product[0], order, item_data.quantity)
            entities_to_save.append(product[0])

        # Сохраняем все изменения
        await self.order_repo.save_all(entities_to_save)

        # Получаем заказ с загруженными связями
        order = await self.order_repo.get_order_with_relations(order.id)
        return order

    async def update_order_item(self, data: UpdateOrderDTO) -> OrderItem:
        """
        Обновить количество товара в заказе
        
        Args:
            data: Данные для обновления заказа
            
        Returns:
            Обновленный элемент заказа
            
        Raises:
            NotFoundError: Если заказ, товар или элемент заказа не найдены
            InsufficientStockError: Если недостаточно товара на складе
            BusinessRuleError: Если нарушены бизнес-правила
        """
        # Получаем заказ с товарами
        order = await self.order_repo.get_by_id(data.order_id)
        if not order:
            raise NotFoundError(f"Order with id {data.order_id} not found")

        # Получаем товар
        product = await self.product_repo.get_by_id(data.product_id)
        if not product:
            raise NotFoundError(f"Product with id {data.product_id} not found")

        # Ищем товар в заказе
        existing_item = await self.order_repo.get_order_item(data.order_id, data.product_id)
        if not existing_item:
            raise NotFoundError(f"Product {data.product_id} not found in order {data.order_id}")

        # Проверяем бизнес-правила
        difference = data.quantity - existing_item.product_quantity
        if difference < 0:
            difference = 0
        self._validate_order_update(product, difference)

        # Применяем изменения
        self._apply_order_changes(existing_item, product, order, data.quantity)

        await self.order_repo.save_all([existing_item, product, order])

        return existing_item

    async def get_order_by_id(self, order_id: int) -> Order:
        """
        Получить заказ по ID с загруженными связями
        
        Args:
            order_id: ID заказа
            
        Returns:
            Заказ с загруженными связями
            
        Raises:
            NotFoundError: Если заказ не найден
        """
        order = await self.order_repo.get_order_with_relations(order_id)
        if not order:
            raise NotFoundError(f"Order with id {order_id} not found")
        
        return order

    async def get_all_orders(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Получить все заказы с загруженными связями
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список заказов с загруженными связями
        """
        return await self.order_repo.get_all_with_relations(skip, limit)

    async def delete_order(self, order_id: int) -> None:
        """
        Удалить товар из заказа с возвратом на склад
        
        Args:
            order_id: ID заказа
            product_id: ID товара

        Raises:
            NotFoundError: Если заказ, товар или элемент заказа не найдены
        """
        # Получаем заказ
        order = await self.order_repo.get_order_with_relations(order_id)
        if not order:
            raise NotFoundError(f"Order with id {order_id} not found")

        # Получаем товар
        products = []
        for order_item in order.product_items:
            product = order_item.product
            # Возвращаем товар на склад
            product.storage_quantity += order_item.product_quantity
            products.append(product)

        # Сохраняем изменения и удаляем элемент заказа
        await self.order_repo.save_all(products)
        await self.order_repo.delete_order(order)

    def _validate_order_update(self, product, quantity: int) -> None:
        """
        Валидация бизнес-правил при обновлении заказа

        Args:
            product: Товар
            quantity: Изменение количества (для нового элемента - это начальное количество)

        Raises:
            BusinessRuleError: Если количество не положительное
            InsufficientStockError: Если недостаточно товара на складе
        """
        # Проверяем, что количество положительное
        if quantity < 0:
            raise BusinessRuleError("Order item quantity must be positive")

        # Проверяем доступность на складе
        if quantity > product.storage_quantity:
            raise InsufficientStockError(
                f"Not enough stock for product {product.name}. "
                f"Available: {product.storage_quantity}, "
                f"Requested: {quantity}"
            )

    def _apply_order_changes(self, order_item: OrderItem,
                             product, order, quantity: int) -> None:
        """
        Применить изменения к заказу и товару (подсчёт общего количества в заказе и на складе)

        Args:
            order_item: Элемент заказа для обновления
            product: Товар для обновления остатков
            order: Заказ для обновления общего количества
            quantity: Изменение количества (может быть отрицательным, для нового элемента - начальное количество)
        """
        difference = quantity - order_item.product_quantity
        order_item.product_quantity = quantity

        # Обновляем остаток на складе уменьшаем при добавлении
        product.storage_quantity -= difference

        order.total_quantity += difference

_order_services = None

def get_order_services():
    global _order_services

    if _order_services is None:
        _order_services = OrderService

    return _order_services
