import traceback

from fastapi import APIRouter, Depends, HTTPException

from src.dependencies import get_order_service
from src.exceptions import NotFoundError, InsufficientStockError
from src.schemas.order import UpdateOrderDTO
from src.services.order_service import OrderService

router = APIRouter()


@router.put("/update_order/{order_id}")
async def update_order(
        data: UpdateOrderDTO,
        order_service: OrderService = Depends(get_order_service),
):
    try:
        result = await order_service.update_order_item(data)
        return {
            "message": "Order updated successfully",
            "order_item": {
                "id": result.id,
                "order_id": result.order_id,
                "product_id": result.product_id,
                "quantity": result.product_quantity
            }
        }

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Order or product not found")
    except InsufficientStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")
