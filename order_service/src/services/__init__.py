from src.services.order_service import get_order_services, OrderService

OrderService: OrderService = get_order_services()

__all__ = [
    "OrderService"
]
