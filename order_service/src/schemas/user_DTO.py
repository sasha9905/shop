import uuid

from pydantic import BaseModel


class UserBase(BaseModel):
    id: uuid.UUID



class UserAll(UserBase):
    username: str
