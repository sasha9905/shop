"""
Схемы для пользователей (для синхронизации с auth_service)
"""
import uuid

from pydantic import BaseModel

from src.models import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя с ID"""
    id: uuid.UUID


class UserAll(UserBase):
    """Полная схема пользователя для синхронизации"""
    username: str
    role: UserRole

