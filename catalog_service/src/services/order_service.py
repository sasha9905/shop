from src.repositories import OrderRepository
from src.repositories import ProductRepository
from src.models import OrderItem
from src.exceptions import NotFoundError, InsufficientStockError, BusinessRuleError
from src.schemas.order import UpdateOrderDTO


class OrderService:
    def __init__(self, order_repository: OrderRepository,
                 product_repository: ProductRepository):
        self.order_repo = order_repository
        self.product_repo = product_repository

    async def update_order_item(self, data: UpdateOrderDTO) -> OrderItem:
        """
        Обновить количество товара в заказе
        """
        # Получаем заказ с товарами
        order = await self.order_repo.get_by_id(data.order_id)
        if not order:
            raise NotFoundError(f"Order with id {data.order_id} not found")

        # Получаем товар с блокировкой
        product = await self.product_repo.get_by_id(data.product_id)
        if not product:
            raise NotFoundError(f"Product with id {data.product_id} not found")

        # Ищем товар в заказе
        existing_item = await self.order_repo.get_order_item(data.order_id, data.product_id)
        if not existing_item:
            raise NotFoundError(f"Product {data.product_id} not found in order {data.order_id}")

        # Получаем заказ для обновления total_quantity
        order = await self.order_repo.get_by_id(data.order_id)
        if not order:
            raise NotFoundError(f"Order with id {data.order_id} not found")

        # Проверяем бизнес-правила
        self._validate_order_update(existing_item, product, data.quantity)

        # Применяем изменения
        self._apply_order_changes(existing_item, product, order, data.quantity)

        await self.order_repo.save_all([existing_item, product, order])

        return existing_item

    def _validate_order_update(self, order_item: OrderItem,
                                        product, quantity: int) -> None:
        """Валидация бизнес-правил"""

        # Проверяем, что quantity положительное
        if quantity <= 0:
            raise BusinessRuleError("Quantity must be positive")

        # Рассчитываем новое количество
        new_quantity = order_item.product_quantity + quantity

        # Проверяем доступность на складе
        if new_quantity > product.storage_quantity:
            raise InsufficientStockError(
                f"Not enough stock for product {product.name}. "
                f"Available: {product.storage_quantity}, "
                f"Requested: {new_quantity}"
            )

    def _apply_order_changes(self, order_item: OrderItem,
                                   product, order, quantity: int) -> None:
        """Применить изменения к заказу и товару"""

        # Обновляем количество в заказе
        order_item.product_quantity += quantity

        # Обновляем остаток на складе
        product.storage_quantity -= quantity

        # Обновляем общее количество в заказе
        order.total_quantity += quantity

_order_services = None

def get_order_services():
    global _order_services

    if _order_services is None:
        _order_services = OrderService

    return _order_services
