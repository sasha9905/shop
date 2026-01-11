from fastapi import APIRouter, Depends, HTTPException, status
from faststream.rabbit import RabbitExchange, ExchangeType
from faststream.rabbit.fastapi import RabbitRouter

from src.core import get_auth_service, get_user_service
from src.core.logging_config import logger
from src.config import get_settings
from src.schemas import Token, LoginRequest, UserCreate, UserResponse, UserEvent
from src.services import AuthService, UserService
from src.exceptions import AlreadyExistError, AuthenticationError, NotFoundError

settings = get_settings()
router = RabbitRouter(settings.rabbitmq_url, prefix="/auth")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserCreate,
        user_service: UserService = Depends(get_user_service)
):
    """
    Регистрация нового пользователя
    
    Args:
        user_data: Данные для регистрации
        user_service: Сервис для работы с пользователями
        
    Returns:
        UserResponse: Созданный пользователь
        
    Raises:
        HTTPException 400: Если email или username уже заняты
    """
    try:
        user = await user_service.create_user(user_data)

        user_event = UserEvent(
            id=user.id,
            username=user.username,
            role=user.role
        )

        # Отправка события в RabbitMQ
        logger.info(f"User created successfully: {user.id} - {user.username}")
        await router.broker.publish(
            message=user_event.model_dump(),
            exchange=RabbitExchange(name="user_created", type=ExchangeType.FANOUT),
        )
        return user

    except NotFoundError as e:
        logger.warning(f"User logging is failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except AlreadyExistError as e:
        logger.warning(f"User creating is failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in register: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", response_model=Token)
async def login(
        login_data: LoginRequest,
        auth_service: AuthService = Depends(get_auth_service)
):
    """
    Авторизация пользователя
    
    Args:
        login_data: Данные для авторизации (username, password)
        auth_service: Сервис аутентификации
        
    Returns:
        Token: JWT токен
        
    Raises:
        HTTPException 401: Если неверный username или password
    """
    try:
        user = await auth_service.authenticate_user(
            login_data.username,
            login_data.password
        )
        token = await auth_service.create_token(user)

        logger.info(f"User logged in successfully: {user.id} - {user.username}")
        return token

    except NotFoundError as e:
        logger.warning(f"User logging is failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except AuthenticationError as e:
        logger.warning(f"Authentification failed: {str(e)}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/verify")
async def verify_token(
        token: str,
        auth_service: AuthService = Depends(get_auth_service)
):
    """
    Верификация токена (для других сервисов)
    
    Args:
        token: JWT токен для проверки
        auth_service: Сервис аутентификации
        
    Returns:
        dict: Результат проверки токена с информацией о пользователе
    """
    try:
        logger.info("Token verification request received")
        result = await auth_service.verify_token(token)

        if result:
            user, payload = result  # Распаковываем результат
            logger.info(f"Token is valid for user: {user.id} - {user.username}")
            return {
                "valid": True,
                "user_id": str(user.id),
                "role": user.role.value,
                "username": user.username
            }

        logger.warning("Token verification failed: invalid token")
        return {"valid": False}
    except Exception as e:
        logger.error(f"Error in verify_token: {str(e)}", exc_info=True)
        return {"valid": False}
