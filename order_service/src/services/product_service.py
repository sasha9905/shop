from src.repositories import ProductRepository
from src.models import Product
from src.schemas import ProductAddDTO


class ProductService:
    """
    Сервис для работы с товарами
    """
    
    def __init__(self, product_repository: ProductRepository):
        """
        Инициализация сервиса
        
        Args:
            product_repository: Репозиторий для работы с товарами
        """
        self.product_repo = product_repository

    async def create_product(self, data: ProductAddDTO) -> Product:
        """
        Создать новый товар
        
        Args:
            data: Данные товара для создания
            
        Returns:
            Созданный товар
        """
        product = Product(
            name=data.name,
            price=data.price,
            storage_quantity=data.quantity
        )
        return await self.product_repo.create(product)

