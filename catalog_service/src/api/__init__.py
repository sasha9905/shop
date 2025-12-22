from fastapi import APIRouter

from src.api.categories_api import router as categories_router
from src.api.product_api import router as product_router


router = APIRouter()

router.include_router(categories_router)
router.include_router(product_router)

__all__ = [
    "router",
]
