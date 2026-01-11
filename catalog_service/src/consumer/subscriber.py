from fastapi import Depends, HTTPException, status
from faststream.rabbit import RabbitExchange, ExchangeType
from faststream.rabbit.fastapi import RabbitRouter

from src.core import get_user_service
from src.core.logging_config import logger
from src.config import get_settings
from src.services import UserService
from src.schemas import UserBase, UserAll
from src.exceptions import NotFoundError

settings = get_settings()
router = RabbitRouter(settings.rabbitmq_url)


@router.subscriber(
    exchange=RabbitExchange(name="user_created", type=ExchangeType.FANOUT),
    queue="catalog_user_created",
)
async def handle_user_created(
    user_data: UserAll,
    user_service: UserService = Depends(get_user_service)
):
    """
    Обработка события создания пользователя из auth_service
    
    Args:
        user_data: Данные пользователя для создания
        user_service: Сервис для работы с пользователями
        
    Raises:
        HTTPException 400: Если пользователь уже существует
    """
    try:
        logger.info(f"User creation event received in catalog service: {user_data.username}")
        # Создаем пользователя
        await user_service.create_user(user_data)
        logger.info(f"User created successfully in catalog service: {user_data.id} - {user_data.username}")
    except NotFoundError as e:
        logger.warning(f"Category creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        logger.warning(f"User creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in handle_user_created: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.subscriber(
    exchange=RabbitExchange(name="user_updated", type=ExchangeType.FANOUT),
    queue="catalog_user_updated",
)
async def handle_user_updated(
    user_data: UserAll,
    user_service: UserService = Depends(get_user_service)
):
    """
    Обработка события обновления пользователя из auth_service
    
    Args:
        user_data: Данные пользователя для обновления
        user_service: Сервис для работы с пользователями
        
    Raises:
        HTTPException 404: Если пользователь не найден
    """
    try:
        logger.info(f"User update event received in catalog service: {user_data.username}")
        updated_user = await user_service.update_user(user_data)
        if not updated_user:
            logger.warning(f"Failed to update user: {user_data.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User updated successfully in catalog service: {user_data.id} - {user_data.username}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in handle_user_updated: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.subscriber(
    exchange=RabbitExchange(name="user_deleted", type=ExchangeType.FANOUT),
    queue="catalog_user_deleted",
)
async def handle_user_deleted(
    user: UserBase,
    user_service: UserService = Depends(get_user_service)
):
    """
    Обработка события удаления пользователя из auth_service
    
    Args:
        user: Данные пользователя для удаления (только ID)
        user_service: Сервис для работы с пользователями
        
    Raises:
        HTTPException 404: Если пользователь не найден
        HTTPException 500: При внутренней ошибке сервера
    """
    try:
        logger.info(f"User deletion event received in catalog service: {user.id}")
        
        # Удаляем пользователя через сервис
        success = await user_service.delete_user(user.id)
        if not success:
            logger.warning(f"User not found for deletion: {user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User deleted successfully in catalog service: {user.id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in handle_user_deleted: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
