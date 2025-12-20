from typing import Optional

from sqlalchemy import select

from src.repositories.base_repository import BaseRepository
from src.models import Product


class ProductRepository(BaseRepository):

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Получить товар по ID"""
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
