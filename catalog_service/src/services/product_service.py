from typing import List, Optional

from src.repositories import ProductRepository, CategoryRepository
from src.models import Product
from src.schemas import ProductAddDTO
from src.exceptions import NotFoundError


class ProductService:
    """
    Сервис для работы с товарами
    """
    
    def __init__(self, product_repository: ProductRepository, category_repository: CategoryRepository):
        """
        Инициализация сервиса
        
        Args:
            product_repository: Репозиторий для работы с товарами
            category_repository: Репозиторий для работы с категориями
        """
        self.product_repo = product_repository
        self.category_repo = category_repository

    async def create_product(self, data: ProductAddDTO) -> Product:
        """
        Создать новый товар
        
        Args:
            data: Данные товара для создания
            
        Returns:
            Созданный товар
            
        Raises:
            NotFoundError: Если категория не найдена
        """
        # Проверяем существование категории
        category = await self.category_repo.get_by_id(data.category_id)
        if not category:
            raise NotFoundError(f"Category with id {data.category_id} not found")
        
        product = Product(
            name=data.name,
            price=data.price,
            storage_quantity=data.quantity,
            category_id=data.category_id
        )
        return await self.product_repo.create(product)

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Получить товар по ID
        
        Args:
            product_id: ID товара
            
        Returns:
            Product или None, если товар не найден
        """
        return await self.product_repo.get_by_id(product_id)

    async def get_all_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Получить список всех товаров
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список товаров
        """
        return await self.product_repo.get_all(skip, limit)

    async def get_products_by_category_id(self, category_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Получить товары по категории
        
        Args:
            category_id: ID категории
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список товаров в категории
        """
        return await self.product_repo.get_by_category_id(category_id, skip, limit)

