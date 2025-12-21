from fastapi import APIRouter

from src.api.auth_api import router as auth_router
from src.api.user_api import router as user_router


router = APIRouter()

router.include_router(auth_router)
router.include_router(user_router)

__all__ = [
    "router",
]
