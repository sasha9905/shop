from typing import List, Optional

from src.repositories import CategoryRepository
from src.models import Category
from src.schemas import CategoryAddDTO
from src.exceptions import NotFoundError


class CategoryService:
    """
    Сервис для работы с категориями
    """
    
    def __init__(self, category_repository: CategoryRepository):
        """
        Инициализация сервиса
        
        Args:
            category_repository: Репозиторий для работы с категориями
        """
        self.category_repo = category_repository

    async def create_category(self, data: CategoryAddDTO) -> Category:
        """
        Создать новую категорию
        
        Args:
            data: Данные категории для создания
            
        Returns:
            Созданная категория
            
        Raises:
            NotFoundError: Если родительская категория не найдена
        """
        level = 0
        parent_id = data.parent_id
        
        # Нормализуем parent_id (0 или None означает корневую категорию)
        if parent_id == 0 or not parent_id:
            parent_id = None
        
        # Если есть родительская категория, вычисляем уровень
        if parent_id:
            parent_category = await self.category_repo.get_by_id(parent_id)
            if not parent_category:
                raise NotFoundError(f"Parent category with id {parent_id} not found")
            level = parent_category.level + 1
        
        category = Category(
            name=data.name,
            parent_id=parent_id,
            level=level
        )
        return await self.category_repo.create(category)

    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """
        Получить категорию по ID
        
        Args:
            category_id: ID категории
            
        Returns:
            Category или None, если категория не найдена
        """
        return await self.category_repo.get_by_id(category_id)

    async def get_all_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """
        Получить список всех категорий
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список категорий
        """
        return await self.category_repo.get_all(skip, limit)

