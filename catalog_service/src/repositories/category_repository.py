from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.repositories.base_repository import BaseRepository
from src.models import Category


class CategoryRepository(BaseRepository):
    """
    Репозиторий для работы с категориями
    """
    
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """
        Получить категорию по ID
        
        Args:
            category_id: ID категории
            
        Returns:
            Category или None, если категория не найдена
        """
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(self, category_id: int) -> Optional[Category]:
        """
        Получить категорию по ID с загруженными связями (parent, children, products)
        
        Args:
            category_id: ID категории
            
        Returns:
            Category с загруженными связями или None, если категория не найдена
        """
        result = await self.session.execute(
            select(Category)
            .where(Category.id == category_id)
            .options(
                selectinload(Category.parent),
                selectinload(Category.children),
                selectinload(Category.products)
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """
        Получить список всех категорий
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список категорий
        """
        result = await self.session.execute(
            select(Category).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, category: Category) -> Category:
        """
        Создать новую категорию
        
        Args:
            category: Объект категории для создания
            
        Returns:
            Созданная категория
        """
        return (await self.save_all([category]))[0]

