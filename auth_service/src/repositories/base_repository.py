from abc import ABC
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_all(self, entities):
        """Сохранить несколько entities"""
        for entity in entities:
            self.session.add(entity)
        await self.session.flush()
        for entity in entities:
            await self.session.refresh(entity)
        await self.session.commit()
        return entities
