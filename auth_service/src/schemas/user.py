import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from src.models import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: UserRole


class UserResponse(UserInDB):
    pass