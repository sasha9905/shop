from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, ExpiredSignatureError

from src.services import AuthService
from src.models import User, UserRole
from src.core.db_dependency import get_db_dependency


security = HTTPBearer()
db_dependency_instance = get_db_dependency()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_dependency_instance.get_session():
        yield session


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_db_session)
) -> User:
    auth_service = AuthService(session)
    token = credentials.credentials

    result = await auth_service.verify_token(token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, _ = result
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
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
