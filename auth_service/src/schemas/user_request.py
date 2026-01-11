"""
Схемы для запросов пользователей (входящие данные)
"""
from typing import Optional

from pydantic import BaseModel, EmailStr

from src.models import UserRole


class UserCreate(BaseModel):
    """Схема для создания нового пользователя"""
    email: EmailStr
    username: str
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

