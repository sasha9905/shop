"""
Схемы для товаров
"""
from pydantic import BaseModel


class ProductAddDTO(BaseModel):
    """Схема для создания товара"""
    name: str
    quantity: int
    price: int
    category_id: int

