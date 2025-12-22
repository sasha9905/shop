from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_db_session, publish_event
from src.schemas import Token, LoginRequest
from src.schemas import UserCreate, UserResponse
from src.services import AuthService
from src.services import UserService

router = APIRouter(prefix="/auth", tags=["authentication"])


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

    # Отправка события в RabbitMQ
    await publish_event("user.created", {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "role": user.role
    })

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

    await publish_event("user.logged_in", {
        "user_id": str(user.id),
        "token": token
    })

    return token

# Верификация токена (для других сервисов)
@router.post("/verify")
async def verify_token(token: str, session: AsyncSession = Depends(get_db_session)):
    auth_service = AuthService(session)

    payload = auth_service.verify_token(token)
    if payload:
        return {"valid": True, "user_id": payload["sub"], "role": payload["role"]}
    return {"valid": False}
