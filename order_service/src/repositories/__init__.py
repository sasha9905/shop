from src.repositories.order_repository import get_order_repo, OrderRepository
from src.repositories.product_repository import get_product_repo, ProductRepository
from src.repositories.user_repository import get_user_repo, UserRepository

OrderRepository: OrderRepository = get_order_repo()
ProductRepository: ProductRepository = get_product_repo()
UserRepository: UserRepository = get_user_repo()

__all__ = [
    "OrderRepository",
    "ProductRepository",
    "UserRepository",
]
