from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from db_dependency import db_dependency
from src.repositories.order_repository import OrderRepository
from src.repositories.product_repository import ProductRepository
from src.services.order_service import OrderService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_dependency.get_session():
        yield session


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
