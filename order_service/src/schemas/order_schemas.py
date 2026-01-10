import uuid
from typing import List

from pydantic import BaseModel, Field


# Request DTOs
class OrderItemAddDTO(BaseModel):
    """DTO для добавления элемента заказа"""
    product_id: int = Field(gt=0, description="ID товара должен быть положительным")
    quantity: int = Field(gt=0, description="Количество товара должно быть больше 0")


class OrderAddDTO(BaseModel):
    """DTO для создания заказа"""
    user_id: uuid.UUID
    items: list[OrderItemAddDTO] = Field(min_length=1, description="Заказ должен содержать хотя бы один товар")


class UpdateOrderDTO(BaseModel):
    """DTO для обновления заказа"""
    order_id: int = Field(gt=0, description="ID заказа должен быть положительным")
    product_id: int = Field(gt=0, description="ID товара должен быть положительным")
    quantity: int = Field(description="Изменение количества товара (может быть положительным или отрицательным)")


class ProductAddDTO(BaseModel):
    """DTO для добавления товара"""
    name: str
    quantity: int = Field(gt=0, description="Количество товара должно быть больше 0")
    price: int = Field(ge=0, description="Цена товара должна быть неотрицательной")


# Response DTOs
class OrderItemResponseDTO(BaseModel):
    """Схема ответа для элемента заказа"""
    id: int
    order_id: int
    product_id: int
    product_name: str
    quantity: int
    price: int


class OrderResponseDTO(BaseModel):
    """Схема ответа для заказа"""
    id: int
    user_id: uuid.UUID
    client_name: str
    user_quantity: int
    items: List[OrderItemResponseDTO]


class OrderDetailResponseDTO(BaseModel):
    """Схема ответа для детальной информации о заказе"""
    id: int
    client_id: uuid.UUID
    client_name: str
    total_quantity: int
    items: List[OrderItemResponseDTO]


class OrderItemUpdateResponseDTO(BaseModel):
    """Схема ответа для обновления элемента заказа"""
    id: int
    order_id: int
    product_id: int
    quantity: int


class OrderUpdateResponseDTO(BaseModel):
    """Схема ответа для обновления заказа"""
    message: str
    order_item: OrderItemUpdateResponseDTO


class OrdersListResponseDTO(BaseModel):
    """Схема ответа для списка заказов"""
    orders: List[OrderDetailResponseDTO]
    total: int

