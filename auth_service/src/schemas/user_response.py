"""
Схемы для ответов пользователей (исходящие данные)
"""
import uuid

from pydantic import BaseModel, ConfigDict

from src.models import UserRole


class UserResponse(BaseModel):
    """Схема для ответа с данными пользователя"""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    username: str
    role: UserRole


class UserEventID(BaseModel):
    """Схема для события с ID пользователя"""
    id: uuid.UUID


class UserEvent(UserEventID):
    """Схема для события создания/обновления пользователя"""
    username: str
    role: UserRole

