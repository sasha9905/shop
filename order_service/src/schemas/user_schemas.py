import uuid

from pydantic import BaseModel


# Request DTOs
class UserBase(BaseModel):
    """Базовый DTO для пользователя"""
    id: uuid.UUID


class UserAll(BaseModel):
    """DTO для пользователя со всеми полями"""
    id: uuid.UUID
    username: str

