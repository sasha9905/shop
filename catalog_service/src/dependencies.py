from typing import AsyncGenerator

import httpx
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import UserService
from src.database import db_dependency_instance

security = HTTPBearer()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_dependency_instance.get_session():
        yield session

async def get_user_service(
    session: AsyncSession = Depends(get_db_session)
) -> UserService:
    """Dependency для UserService"""
    return UserService(session)


async def verify_token_with_auth_service(token: str) -> dict:
    """Проверка токена через HTTP запрос к auth-service"""
    async with httpx.AsyncClient() as client:
        try:
            print(1)
            response = await client.post(
                "http://localhost:8000/api/v1/verify",
                params={"token": token}
            )
            return response.json()
        except:
            return {"valid": False}

async def get_current_user(token: str = Depends(security)):
    print(123)
    result = await verify_token_with_auth_service(token.credentials)
    if not result.get("valid", False):
        raise HTTPException(status_code=401, detail="Invalid token")
    return result
