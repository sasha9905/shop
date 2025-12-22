from typing import Optional

from pydantic import BaseModel


class CategoryAddDTO(BaseModel):
    name: str
    parent_id: Optional[int]


class ProductAddDTO(BaseModel):
    name: str
    quantity: int
    price: int
    category_id: int


class UpdateOrderDTO(BaseModel):
    order_id: int
    product_id: int