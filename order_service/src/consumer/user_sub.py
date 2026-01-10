from fastapi import Depends, HTTPException, status
from faststream.rabbit import RabbitExchange, ExchangeType
from faststream.rabbit.fastapi import RabbitRouter

from src.config import get_settings
from src.core import get_user_service
from src.core.logging_config import logger
from src.services import UserService
from src.schemas import UserBase, UserAll

settings = get_settings()

router = RabbitRouter(settings.rabbitmq_url)


@router.subscriber(
    exchange=RabbitExchange(name="user_created", type=ExchangeType.FANOUT),
    queue="order_user_created",
)
async def handle_user_created(
        user_data: UserAll,
        user_service: UserService = Depends(get_user_service)
):
    """
    Обработка события создания пользователя
    
    Args:
        user_data: Данные пользователя для создания
        user_service: Сервис для работы с пользователями
    """
    try:
        logger.info(f"New user received in order service: {user_data.username}")
        existing_user = await user_service.get_user_by_username(user_data.username)
        if existing_user:
            logger.warning(f"User already exists: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        await user_service.create_user(user_data)
        logger.info(f"User created successfully: {user_data.id} - {user_data.username}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.subscriber(
    exchange=RabbitExchange(name="user_updated", type=ExchangeType.FANOUT),
    queue="order_user_updated",
)
async def handle_user_updated(
        user_data: UserAll,
        user_service: UserService = Depends(get_user_service)
):
    """
    Обработка события обновления пользователя
    
    Args:
        user_data: Данные пользователя для обновления
        user_service: Сервис для работы с пользователями
    """
    try:
        logger.info(f"User update received in order service: {user_data.username}")
        
        existing_user = await user_service.get_user_by_id(user_data.id)
        if not existing_user:
            logger.warning(f"User not found for update: {user_data.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        updated_user = await user_service.update_user(user_data)
        if not updated_user:
            logger.warning(f"Failed to update user: {user_data.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User updated successfully: {user_data.id} - {user_data.username}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.subscriber(
    exchange=RabbitExchange(name="user_deleted", type=ExchangeType.FANOUT),
    queue="order_user_deleted",
)
async def handle_user_deleted(
        user: UserBase,
        user_service: UserService = Depends(get_user_service)
):
    """
    Обработка события удаления пользователя
    
    Args:
        user: Данные пользователя для удаления
        user_service: Сервис для работы с пользователями
    """
    try:
        logger.info(f"User deletion received in order service: {user.id}")
        success = await user_service.delete_user(user.id)
        if not success:
            logger.warning(f"User not found for deletion: {user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User deleted successfully: {user.id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
