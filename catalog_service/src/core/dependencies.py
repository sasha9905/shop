from typing import AsyncGenerator

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import UserRepository, ProductRepository, CategoryRepository
from src.services import UserService, ProductService, CategoryService
from src.models import UserRole, User
from src.database import db_dependency_instance
from src.core.security import verify_token_with_auth_service

security = HTTPBearer()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_dependency_instance.get_session():
        yield session


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    """Dependency для UserRepository"""
    return UserRepository(session)


async def get_category_repository(
    session: AsyncSession = Depends(get_db_session)
) -> CategoryRepository:
    """Dependency для CategoryRepository"""
    return CategoryRepository(session)


async def get_product_repository(
    session: AsyncSession = Depends(get_db_session)
) -> ProductRepository:
    """Dependency для ProductRepository"""
    return ProductRepository(session)


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    """Dependency для UserService"""
    return UserService(user_repo)


async def get_category_service(
    category_repo: CategoryRepository = Depends(get_category_repository)
) -> CategoryService:
    """Dependency для CategoryService"""
    return CategoryService(category_repo)


async def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
    category_repo: CategoryRepository = Depends(get_category_repository)
) -> ProductService:
    """Dependency для ProductService"""
    return ProductService(product_repo, category_repo)


async def get_current_user(token: str = Depends(security)):
    """
    Получить текущего пользователя из токена
    
    Args:
        token: HTTP Bearer токен
        
    Returns:
        User: Текущий пользователь
        
    Raises:
        HTTPException: Если токен невалидный
    """
    result = await verify_token_with_auth_service(token.credentials)
    if not result.get("valid", False):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = User(
        id=result.get("user_id"),
        role=result.get("role"),
        username=result.get("username")
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
