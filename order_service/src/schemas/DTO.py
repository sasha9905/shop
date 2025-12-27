import uuid
from datetime import datetime

from pydantic import BaseModel


class ProductAddDTO(BaseModel):
    name: str
    quantity: int
    price: int


class OrderItemAddDTO(BaseModel):
    product_id: int
    quantity: int


class OrderAddDTO(BaseModel):
    user_id: uuid.UUID
    created_at: datetime
    items: list[OrderItemAddDTO]


class UpdateOrderDTO(BaseModel):
    order_id: int
    product_id: int