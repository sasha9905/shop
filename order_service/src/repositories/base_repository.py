from abc import ABC
from contextlib import asynccontextmanager
from typing import List, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging_config import logger


class BaseRepository(ABC):
    """
    Базовый репозиторий с транзакционной поддержкой
    """
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория
        
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        self.session = session

    @asynccontextmanager
    async def transaction(self):
        """
        Контекстный менеджер для транзакций с автоматическим откатом при ошибках
        
        Usage:
            async with self.transaction():
                # операции с БД
        """
        try:
            yield self.session
            await self.session.commit()
        except Exception as e:
            logger.error(f"Transaction error, rolling back: {str(e)}", exc_info=True)
            await self.session.rollback()
            raise

    async def save_all(self, entities: List[Any]):
        """
        Сохранить несколько entities в транзакции
        
        Args:
            entities: Список сущностей для сохранения
            
        Returns:
            Список сохраненных сущностей
            
        Raises:
            Exception: При ошибке выполняется откат транзакции
        """
        async with self.transaction():
            for entity in entities:
                self.session.add(entity)
            await self.session.flush()
            for entity in entities:
                await self.session.refresh(entity)
        return entities
