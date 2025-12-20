from pydantic import BaseModel


class UpdateOrderDTO(BaseModel):
    order_id: int
    product_id: int
    quantity: int
