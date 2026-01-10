from fastapi import Depends, HTTPException, status

from faststream.rabbit.fastapi import RabbitRouter

from src.config import get_settings
from src.core import get_product_service
from src.core.logging_config import logger
from src.schemas import ProductAddDTO
from src.services.product_service import ProductService

settings = get_settings()

router = RabbitRouter(settings.rabbitmq_url)


@router.subscriber("product.created")
async def handle_product_created(
        data: ProductAddDTO,
        product_service: ProductService = Depends(get_product_service)
):
    """
    Обработка события создания товара
    
    Args:
        data: Данные товара для создания
        product_service: Сервис для работы с товарами
    """
    try:
        logger.info(f"New product received in order service: {data.name}")
        product = await product_service.create_product(data)
        logger.info(f"Product created successfully: {product.id} - {product.name}")
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
