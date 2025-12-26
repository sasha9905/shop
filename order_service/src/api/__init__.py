from fastapi import APIRouter

from src.api.order_api import router as change_order_router
from src.consumer import user_sub, product_sub


router = APIRouter()

router.include_router(change_order_router)
router.include_router(user_sub)
router.include_router(product_sub)

__all__ = [
    "router",
]
