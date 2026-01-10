import uuid
from typing import Optional, List

from src.repositories import UserRepository
from src.models import User
from src.schemas import UserAll


class UserService:
    """
    Сервис для работы с пользователями
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Инициализация сервиса
        
        Args:
            user_repository: Репозиторий для работы с пользователями
        """
        self.user_repo = user_repository

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Получить пользователя по ID
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            User или None, если пользователь не найден
        """
        return await self.user_repo.get_by_id(user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Получить пользователя по имени пользователя
        
        Args:
            username: Имя пользователя
            
        Returns:
            User или None, если пользователь не найден
        """
        return await self.user_repo.get_by_username(username)

    async def create_user(self, user_data: UserAll) -> User:
        """
        Создать нового пользователя
        
        Args:
            user_data: Данные пользователя для создания
            
        Returns:
            Созданный пользователь
            
        Raises:
            ValueError: Если пользователь с таким ID уже существует
        """
        # Проверяем, не существует ли уже пользователь с таким ID
        existing_user = await self.user_repo.get_by_id(user_data.id)
        if existing_user:
            raise ValueError(f"User with id {user_data.id} already exists")
        
        db_user = User(
            id=user_data.id,
            username=user_data.username
        )
        return await self.user_repo.create(db_user)

    async def update_user(self, user_data: UserAll) -> Optional[User]:
        """
        Обновить данные пользователя
        
        Args:
            user_data: Данные пользователя для обновления
            
        Returns:
            Обновленный User или None, если пользователь не найден
        """
        update_data = user_data.model_dump(exclude_unset=True)
        return await self.user_repo.update(user_data.id, update_data)

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Удалить пользователя
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            True, если пользователь был удален, False если не найден
        """
        return await self.user_repo.delete(user_id)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получить список пользователей с пагинацией
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список пользователей
        """
        return await self.user_repo.get_all(skip, limit)
