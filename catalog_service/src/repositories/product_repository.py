from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.repositories.base_repository import BaseRepository
from src.models import Product, Category


class ProductRepository(BaseRepository):
    """
    Репозиторий для работы с товарами
    """
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Получить товар по ID
        
        Args:
            product_id: ID товара
            
        Returns:
            Product или None, если товар не найден
        """
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_category(self, product_id: int) -> Optional[Product]:
        """
        Получить товар по ID с загруженной категорией
        
        Args:
            product_id: ID товара
            
        Returns:
            Product с загруженной категорией или None, если товар не найден
        """
        result = await self.session.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.category))
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Получить список всех товаров
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список товаров
        """
        result = await self.session.execute(
            select(Product).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_category_id(self, category_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Получить товары по категории
        
        Args:
            category_id: ID категории
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список товаров в категории
        """
        result = await self.session.execute(
            select(Product)
            .where(Product.category_id == category_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, product: Product) -> Product:
        """
        Создать новый товар
        
        Args:
            product: Объект товара для создания
            
        Returns:
            Созданный товар
        """
        return (await self.save_all([product]))[0]

