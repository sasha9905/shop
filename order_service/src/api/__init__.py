from fastapi import APIRouter

from src.api.order_api import router as change_order_router


router = APIRouter()

router.include_router(change_order_router)

__all__ = [
    "router",
]
