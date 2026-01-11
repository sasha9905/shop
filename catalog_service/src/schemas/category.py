"""
Схемы для категорий
"""
from typing import Optional

from pydantic import BaseModel


class CategoryAddDTO(BaseModel):
    """Схема для создания категории"""
    name: str
    parent_id: Optional[int] = None

