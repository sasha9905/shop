from typing import Optional, List

from sqlalchemy import select

from src.repositories.base_repository import BaseRepository
from src.models import Product


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

    async def get_by_ids(self, product_ids: List[int]) -> List[Product]:
        """
        Получить несколько товаров по списку ID одним запросом
        
        Args:
            product_ids: Список ID товаров
            
        Returns:
            Список товаров
        """
        if not product_ids:
            return []
        
        result = await self.session.execute(
            select(Product).where(Product.id.in_(product_ids))
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

_product_repo = None

def get_product_repo():
    global _product_repo

    if _product_repo is None:
        _product_repo = ProductRepository

    return _product_repo
