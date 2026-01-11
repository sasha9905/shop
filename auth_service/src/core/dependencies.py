from typing import AsyncGenerator

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import UserRepository
from src.services import AuthService, UserService
from src.models import User, UserRole
from src.core.db_dependency import get_db_dependency

security = HTTPBearer()
db_dependency_instance = get_db_dependency()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_dependency_instance.get_session():
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    """Dependency для UserRepository"""
    return UserRepository(session)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    """Dependency для UserService"""
    return UserService(user_repo)


async def get_auth_service(
    user_service: UserService = Depends(get_user_service)
) -> AuthService:
    """Dependency для AuthService"""
    return AuthService(user_service)


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Получить текущего пользователя из токена
    
    Args:
        credentials: HTTP авторизационные данные
        auth_service: Сервис аутентификации
        
    Returns:
        User: Текущий пользователь
        
    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    token = credentials.credentials
    result = await auth_service.verify_token(token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, _ = result
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

def require_role(required_role: UserRole):
    """
    Dependency для проверки роли пользователя
    
    Args:
        required_role: Требуемая роль
        
    Returns:
        Функция-проверка роли
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

get_current_admin = require_role(UserRole.ADMIN)
