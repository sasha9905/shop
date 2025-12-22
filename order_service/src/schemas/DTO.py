from datetime import datetime

from pydantic import BaseModel


class ProductAddDTO(BaseModel):
    name: str
    quantity: int
    price: int
    category_id: int


class OrderItemAddDTO(BaseModel):
    product_id: int
    quantity: int


class OrderAddDTO(BaseModel):
    client_id: int
    created_at: datetime
    items: list[OrderItemAddDTO]


class UpdateOrderDTO(BaseModel):
    order_id: int
    product_id: int