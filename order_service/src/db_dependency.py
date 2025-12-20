from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from db_settings import db_settings
from src.base_models.base_classes import Base

class DBDependency:
    def __init__(self) -> None:
        self._engine = create_async_engine(url=db_settings.db_url, echo=db_settings.db_echo)
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
            #await connection.run_sync(Base.metadata.create_all)
            print(Base.metadata.tables.keys())


db_dependency = DBDependency()
