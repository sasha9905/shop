from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import db_dependency_instance


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_dependency_instance.get_session():
        yield session
