from typing import Optional, List

from sqlalchemy import select

from src.repositories.base_repository import BaseRepository
from src.models import User


class UserRepository(BaseRepository):
    """
    Репозиторий для работы с пользователями
    """
    
    async def get_by_id(self, user_id) -> Optional[User]:
        """
        Получить пользователя по ID
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            User или None, если пользователь не найден
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Получить пользователя по имени пользователя
        
        Args:
            username: Имя пользователя
            
        Returns:
            User или None, если пользователь не найден
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """
        Создать нового пользователя
        
        Args:
            user: Объект пользователя для создания
            
        Returns:
            Созданный пользователь
        """
        return (await self.save_all([user]))[0]

    async def update(self, user_id, update_data: dict) -> Optional[User]:
        """
        Обновить данные пользователя
        
        Args:
            user_id: UUID пользователя
            update_data: Словарь с данными для обновления
            
        Returns:
            Обновленный User или None, если пользователь не найден
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # Обновляем поля пользователя
        for key, value in update_data.items():
            setattr(user, key, value)
        
        return (await self.save_all([user]))[0]

    async def delete(self, user_id) -> bool:
        """
        Удалить пользователя
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            True, если пользователь был удален, False если не найден
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        async with self.transaction():
            await self.session.delete(user)
        return True

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получить список пользователей с пагинацией
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список пользователей
        """
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

_user_repo = None

def get_user_repo():
    global _user_repo

    if _user_repo is None:
        _user_repo = UserRepository

    return _user_repo

