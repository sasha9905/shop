from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.core import get_current_admin, get_current_user, get_category_service
from src.core.logging_config import logger
from src.schemas import CategoryAddDTO
from src.services import CategoryService
from src.models import Category, User
from src.exceptions import NotFoundError

router = APIRouter()


@router.post("/category")
async def add_category(
    data: CategoryAddDTO,
    current_user: User = Depends(get_current_admin),
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Создать новую категорию
    
    Args:
        data: Данные категории для создания (name, parent_id)
        current_user: Текущий авторизованный пользователь (администратор)
        category_service: Сервис для работы с категориями
        
    Returns:
        Category: Созданная категория
        
    Raises:
        HTTPException 404: Если родительская категория не найдена
        HTTPException 500: При внутренней ошибке сервера
    """
    try:
        category = await category_service.create_category(data)
        logger.info(f"Category created successfully: {category.id} - {category.name}")
        return {"Message": "Ok", "Category" : category}

    except NotFoundError as e:
        logger.warning(f"Category creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/categories")
async def get_all_categories(
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Получить список всех категорий
    
    Args:
        skip: Количество записей для пропуска (по умолчанию 0)
        limit: Максимальное количество записей (по умолчанию 100)
        user: Текущий авторизованный пользователь
        category_service: Сервис для работы с категориями
        
    Returns:
        List[Category]: Список категорий
    """
    try:
        categories = await category_service.get_all_categories(skip, limit)
        return {"Message": "Ok", "Categories" : categories}

    except Exception as e:
        logger.error(f"Unexpected error in get_all_categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
