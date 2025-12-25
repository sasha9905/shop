import uuid

from pydantic import BaseModel

from src.models import UserRole


class UserBase(BaseModel):
    id: uuid.UUID



class UserAll(UserBase):
    username: str
    role: UserRole
