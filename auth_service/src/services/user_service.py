import uuid
from typing import Optional, List

from src.exceptions import AlreadyExistError, NotFoundError
from src.repositories import UserRepository
from src.models import User
from src.schemas.user_request import UserCreate, UserUpdate
from src.core.security import get_password_hash


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

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            User или None, если пользователь не найден
        """
        return await self.user_repo.get_by_email(email)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Получить пользователя по имени пользователя
        
        Args:
            username: Имя пользователя
            
        Returns:
            User или None, если пользователь не найден
        """
        return await self.user_repo.get_by_username(username)

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

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Создать нового пользователя
        
        Args:
            user_data: Данные пользователя для создания
            
        Returns:
            Созданный пользователь
            
        Raises:
            ValueError: Если пользователь с таким email или username уже существует
        """
        # Check if user exists
        existing_email = await self.get_user_by_email(str(user_data.email))
        if existing_email:
            raise AlreadyExistError(f"Registration failed: email {user_data.email} already taken")

        existing_username = await self.get_user_by_username(user_data.username)
        if existing_username:
            raise AlreadyExistError(f"Registration failed: username {user_data.username} already taken")

        password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password=password
        )
        return await self.user_repo.create(db_user)

    async def update_user(
            self,
            user_id: uuid.UUID,
            user_data: UserUpdate
    ) -> Optional[User]:
        """
        Обновить данные пользователя
        
        Args:
            user_id: UUID пользователя
            user_data: Данные для обновления
            
        Returns:
            Обновленный User или None, если пользователь не найден
        """
        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data.pop("password"))

        if not update_data:
            return await self.get_user_by_id(user_id)

        return await self.user_repo.update(user_id, update_data)

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Удалить пользователя
        
        Args:
            user_id: UUID пользователя
            
        Returns:
            True, если пользователь был удален, False если не найден
        """
        return await self.user_repo.delete(user_id)

