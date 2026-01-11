import uuid
from typing import Optional, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repository import BaseRepository
from src.models import User


class UserRepository(BaseRepository):
    """
    Репозиторий для работы с пользователями
    """
    
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
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

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            User или None, если пользователь не найден
        """
        result = await self.session.execute(
            select(User).where(User.email == email)
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
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        """
        Создать нового пользователя
        
        Args:
            user: Объект пользователя для создания
            
        Returns:
            Созданный пользователь
        """
        return (await self.save_all([user]))[0]

    async def update(self, user_id: uuid.UUID, update_data: dict) -> Optional[User]:
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

    async def delete(self, user_id: uuid.UUID) -> bool:
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

