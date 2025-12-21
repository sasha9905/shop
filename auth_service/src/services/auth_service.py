from datetime import timedelta
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.models import User
from src.schemas import Token
from src.core.security import (
    verify_password,
    create_access_token,
    decode_token
)
from src.services.user_service import UserService


settings = get_settings()

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(session)

    async def authenticate_user(
            self,
            username: str,
            password: str
    ) -> Optional[User]:
        user = await self.user_service.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def create_token(self, user: User) -> Token:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role.value
            },
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token)

    async def verify_token(self, token: str) -> Optional[Tuple[User, dict]]:
        payload = decode_token(token)
        if not payload:
            return None

        user_id = payload.sub
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            return None

        return user, payload.model_dump()