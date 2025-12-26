from src.services.order_service import get_order_services, OrderService
from src.services.user_service import UserService

OrderService: OrderService = get_order_services()

__all__ = [
    "OrderService",
    "UserService",
]
