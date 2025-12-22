from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.config import get_settings
from src.models import Base

db_settings_instance = get_settings()

class DBDependency:
    def __init__(self) -> None:
        self._engine = create_async_engine(url=db_settings_instance.db_url, echo=db_settings_instance.db_echo)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autocommit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @property
    def db_session(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

    async def table_creating(self) -> None:
        async with self._engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)


_db_dependency = None

def get_db_dependency():
    global _db_dependency

    if _db_dependency is None:
        _db_dependency = DBDependency()

    return _db_dependency
