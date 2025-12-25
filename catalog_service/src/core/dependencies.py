from typing import AsyncGenerator

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import UserRole, User
from src.services import UserService
from src.database import db_dependency_instance
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
        role=result.get("role"),
        username=result.get("username")
    )
    return user

def require_role(required_role: UserRole):
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
