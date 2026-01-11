import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from faststream.rabbit import RabbitExchange, ExchangeType
from faststream.rabbit.fastapi import RabbitRouter

from src.core import get_current_user, get_current_admin, get_user_service
from src.core.logging_config import logger
from src.schemas import UserResponse, UserUpdate, UserEvent, UserEventID
from src.services import UserService
from src.models import User
from src.config import get_settings
from src.exceptions import NotFoundError

settings = get_settings()
router = RabbitRouter(settings.rabbitmq_url, prefix="/users")


@router.get("/me", response_model=UserResponse)
async def read_users_me(
        current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о текущем пользователе
    
    Args:
        current_user: Текущий авторизованный пользователь
        
    Returns:
        UserResponse: Информация о текущем пользователе
    """
    return current_user


@router.get("/", response_model=List[UserResponse])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_admin),
        user_service: UserService = Depends(get_user_service)
):
    """
    Получить список всех пользователей (только для администраторов)
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей
        current_user: Текущий авторизованный пользователь (администратор)
        user_service: Сервис для работы с пользователями
        
    Returns:
        List[UserResponse]: Список пользователей
    """
    try:
        users = await user_service.get_all_users(skip, limit)
        return users

    except NotFoundError as e:
        logger.warning(f"User getting is failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in read_users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
        user_id: str,
        current_user: User = Depends(get_current_admin),
        user_service: UserService = Depends(get_user_service)
):
    """
    Получить пользователя по ID (только для администраторов)
    
    Args:
        user_id: UUID пользователя
        current_user: Текущий авторизованный пользователь (администратор)
        user_service: Сервис для работы с пользователями
        
    Returns:
        UserResponse: Информация о пользователе
        
    Raises:
        HTTPException 404: Если пользователь не найден
    """
    try:
        user = await user_service.get_user_by_id(uuid.UUID(user_id))
        return user

    except NotFoundError as e:
        logger.warning(f"User getting is failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError:
        logger.warning(f"Invalid user_id format: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except Exception as e:
        logger.error(f"Unexpected error in read_user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/me", response_model=UserResponse)
async def update_user_me(
        user_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service)
):
    """
    Обновить данные текущего пользователя
    
    Args:
        user_data: Данные для обновления
        current_user: Текущий авторизованный пользователь
        user_service: Сервис для работы с пользователями
        
    Returns:
        UserResponse: Обновленный пользователь
        
    Raises:
        HTTPException 400: Если email или username уже заняты
        HTTPException 404: Если пользователь не найден
    """
    try:
        # Check if email is already taken
        if user_data.email and user_data.email != current_user.email:
            existing_user = await user_service.get_user_by_email(user_data.email)
            if existing_user:
                logger.warning(f"Update failed: email {user_data.email} already registered")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Check if username is already taken
        if user_data.username and user_data.username != current_user.username:
            existing_user = await user_service.get_user_by_username(user_data.username)
            if existing_user:
                logger.warning(f"Update failed: username {user_data.username} already taken")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        updated_user = await user_service.update_user(current_user.id, user_data)
        if not updated_user:
            logger.warning(f"User not found for update: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user_event = UserEvent(
            id=updated_user.id,
            username=updated_user.username,
            role=updated_user.role
        )

        logger.info(f"User updated successfully: {updated_user.id} - {updated_user.username}")
        await router.broker.publish(
            message=user_event.model_dump(),
            exchange=RabbitExchange(name="user_updated", type=ExchangeType.FANOUT)
        )

        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_user_me: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: str,
        current_user: User = Depends(get_current_admin),
        user_service: UserService = Depends(get_user_service)
):
    """
    Удалить пользователя (только для администраторов)
    
    Args:
        user_id: UUID пользователя
        current_user: Текущий авторизованный пользователь (администратор)
        user_service: Сервис для работы с пользователями
        
    Raises:
        HTTPException 404: Если пользователь не найден
    """
    try:
        success = await user_service.delete_user(uuid.UUID(user_id))
        if not success:
            logger.warning(f"User not found for deletion: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user_event_id = UserEventID(id=uuid.UUID(user_id))

        logger.info(f"User deleted successfully: {user_id}")
        await router.broker.publish(
            message=user_event_id.model_dump(),
            exchange=RabbitExchange(name="user_deleted", type=ExchangeType.FANOUT)
        )
        return {"message": "Ok"}

    except NotFoundError as e:
        logger.warning(f"Order creation failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError:
        logger.warning(f"Invalid user_id format: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except Exception as e:
        logger.error(f"Unexpected error in delete_user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
