from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_db_session, get_current_user, get_current_admin, publish_event
from src.schemas import UserResponse, UserUpdate
from src.services import UserService
from src.models import User


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(
        current_user: User = Depends(get_current_user)
):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
        user_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session)
):
    user_service = UserService(session)

    # Check if email is already taken
    if user_data.email and user_data.email != current_user.email:
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Check if username is already taken
    if user_data.username and user_data.username != current_user.username:
        existing_user = await user_service.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    updated_user = await user_service.update_user(current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


@router.get("/", response_model=List[UserResponse])
async def read_users(current_user: User = Depends(get_current_admin),
        session: AsyncSession = Depends(get_db_session)
):
    user_service = UserService(session)
    users = await user_service.get_all_users()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
        user_id: str,
        current_user: User = Depends(get_current_admin),
        session: AsyncSession = Depends(get_db_session)
):
    user_service = UserService(session)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: str,
        current_user: User = Depends(get_current_admin),
        session: AsyncSession = Depends(get_db_session)
):
    user_service = UserService(session)
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
