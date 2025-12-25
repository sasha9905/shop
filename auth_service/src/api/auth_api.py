import logging

from fastapi import APIRouter, Depends, HTTPException, status
from faststream.rabbit.fastapi import RabbitRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_db_session
from src.config import get_settings
from src.schemas import Token, LoginRequest, UserCreate, UserResponse, UserEvent
from src.services import AuthService, UserService

#router = APIRouter(prefix="/auth", tags=["authentication"])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
router = RabbitRouter(settings.rabbitmq_url)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_db_session)
):
    user_service = UserService(session)

    # Check if user exists
    existing_user = await user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_username = await user_service.get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    user = await user_service.create_user(user_data)

    user_event = UserEvent(
        id=user.id,
        username=user.username,
        role=user.role
    )

    # Отправка события в RabbitMQ
    logger.info("User created successfully!")
    await router.broker.publish(message=user_event.model_dump(), queue="user.created")

    return user


@router.post("/login", response_model=Token)
async def login(
        login_data: LoginRequest,
        session: AsyncSession = Depends(get_db_session)
):
    auth_service = AuthService(session)

    user = await auth_service.authenticate_user(
        login_data.username,
        login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = await auth_service.create_token(user)

    logger.info("User logged in successfully!")
    return token

# Верификация токена (для других сервисов)
@router.post("/verify")
async def verify_token(token: str, session: AsyncSession = Depends(get_db_session)):
    auth_service = AuthService(session)

    payload = auth_service.verify_token(token)
    if payload:
        return {"valid": True, "user_id": payload["sub"], "role": payload["role"]}
    return {"valid": False}
