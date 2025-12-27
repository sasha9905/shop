import logging

from fastapi import Depends, HTTPException, status
from faststream.rabbit import RabbitExchange, ExchangeType

from src.core import get_user_service
from faststream.rabbit.fastapi import RabbitRouter

from src.config import get_settings
from src.services import UserService
from src.schemas import UserBase, UserAll

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

router = RabbitRouter(settings.rabbitmq_url)

# Подписчик на события от auth-service
@router.subscriber(
    exchange=RabbitExchange(name="user_created", type=ExchangeType.FANOUT),
    queue="order_user_created",
)
async def handle_user_created(
        user_data: UserAll, user_service:
        UserService = Depends(get_user_service)
):
    """Обработка события создания пользователя"""

    logger.info(f"New user is received in order service: {user_data.username}")
    existing_user = await user_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    # Create new user
    await user_service.create_user(user_data)

    # Отправка события в RabbitMQ
    logger.info("User created successfully!")


@router.subscriber(
    exchange=RabbitExchange(name="user_updated", type=ExchangeType.FANOUT),
    queue="order_user_updated",
)
async def handle_user_created(
        user_data: UserAll, user_service:
        UserService = Depends(get_user_service)
):
    """Обработка события создания пользователя"""
    logger.info(f"User updated in order service: {user_data.username}")

    existing_user = await user_service.get_user_by_id(user_data.id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username not existing"
        )

    updated_user = await user_service.update_user(user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info("User updated successfully!")


@router.subscriber(
    exchange=RabbitExchange(name="user_deleted", type=ExchangeType.FANOUT),
    queue="order_user_deleted",
)
async def handle_user_created(
        user: UserBase,
        user_service: UserService = Depends(get_user_service)
):
    """Обработка события создания пользователя"""
    logger.info(f"New user created in order service: {user.id}")
    success = await user_service.delete_user(user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info("User deleted successfully!")
