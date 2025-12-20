from src.repositories.order_repository import get_order_repo, OrderRepository
from src.repositories.product_repository import get_product_repo, ProductRepository

OrderRepository: OrderRepository = get_order_repo()
ProductRepository: ProductRepository = get_product_repo()

__all__ = [
    "OrderRepository",
    "ProductRepository",
]
