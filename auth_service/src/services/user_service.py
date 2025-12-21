import uuid
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.models import User
from src.schemas.user import UserCreate, UserUpdate
from src.core.security import get_password_hash


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password=password
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def update_user(
            self,
            user_id: uuid.UUID,
            user_data: UserUpdate
    ) -> Optional[User]:
        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data.pop("password"))

        if not update_data:
            return await self.get_user_by_id(user_id)

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
            .returning(User)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
