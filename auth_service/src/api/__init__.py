from fastapi import APIRouter

from src.api.update_order import router as change_order_router


router = APIRouter()

router.include_router(change_order_router)
