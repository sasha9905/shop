from typing import AsyncGenerator

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.services import UserService
from src.database import db_dependency_instance
from src.repositories import OrderRepository
from src.repositories import ProductRepository
from src.services import OrderService
from src.core.security import verify_token_with_auth_service

security = HTTPBearer()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_dependency_instance.get_session():
        yield session


async def get_user_service(
    session: AsyncSession = Depends(get_db_session)
) -> UserService:
    """Dependency для UserService"""
    return UserService(session)


async def get_current_user(token: str = Depends(security)):
    result = await verify_token_with_auth_service(token.credentials)
    if not result.get("valid", False):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = User(
        id=result.get("user_id"),
        username=result.get("username")
    )
    return user


async def get_order_repository(
    session: AsyncSession = Depends(get_db_session)
) -> OrderRepository:
    """Dependency для OrderRepository"""
    return OrderRepository(session)


async def get_product_repository(
    session: AsyncSession = Depends(get_db_session)
) -> ProductRepository:
    """Dependency для ProductRepository"""
    return ProductRepository(session)


async def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    product_repo: ProductRepository = Depends(get_product_repository)
) -> OrderService:
    """Dependency для OrderService"""
    return OrderService(order_repo, product_repo)