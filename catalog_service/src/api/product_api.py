from fastapi import Depends, HTTPException, status
from faststream.rabbit.fastapi import RabbitRouter
from typing import List

from src.config import get_settings
from src.core import get_current_admin, get_current_user, get_product_service
from src.core.logging_config import logger
from src.schemas import ProductAddDTO
from src.services import ProductService
from src.models import Product, User
from src.exceptions import NotFoundError

settings = get_settings()
router = RabbitRouter(settings.rabbitmq_url)


@router.post("/product")
async def create_product(
    data: ProductAddDTO,
    current_user: User = Depends(get_current_admin),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Создать новый товар
    
    Args:
        data: Данные товара для создания (name, quantity, price, category_id)
        current_user: Текущий авторизованный пользователь (администратор)
        product_service: Сервис для работы с товарами
        
    Returns:
        Product: Созданный товар
        
    Raises:
        HTTPException 404: Если категория не найдена
        HTTPException 500: При внутренней ошибке сервера
    """
    try:
        product = await product_service.create_product(data)
        
        # Отправка события в RabbitMQ
        product_DTO = ProductAddDTO(
            name=product.name,
            price=product.price,
            quantity=product.storage_quantity,
            category_id=product.category_id
        )
        await router.broker.publish(
            message=product_DTO.model_dump(),
            queue="product.created"
        )
        logger.info(f"Product created successfully: {product.id} - {product.name}")
        
        return {"Message": "Ok", "Product" : product}

    except NotFoundError as e:
        logger.warning(f"Product creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_product: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/products")
async def get_products(
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Получить список всех товаров
    
    Args:
        skip: Количество записей для пропуска (по умолчанию 0)
        limit: Максимальное количество записей (по умолчанию 100)
        user: Текущий авторизованный пользователь
        product_service: Сервис для работы с товарами
        
    Returns:
        List[Product]: Список товаров
    """
    try:
        products = await product_service.get_all_products(skip, limit)
        return {"Message": "Ok", "Products" : products}

    except Exception as e:
        logger.error(f"Unexpected error in get_products: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/products_with_category/{category_id}")
async def get_products_by_category(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Получить товары по категории
    
    Args:
        category_id: ID категории
        skip: Количество записей для пропуска (по умолчанию 0)
        limit: Максимальное количество записей (по умолчанию 100)
        user: Текущий авторизованный пользователь
        product_service: Сервис для работы с товарами
        
    Returns:
        List[Product]: Список товаров в категории
    """
    try:
        products = await product_service.get_products_by_category_id(category_id, skip, limit)
        return {"Message": "Ok", "Products" : products}

    except Exception as e:
        logger.error(f"Unexpected error in get_products_by_category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
