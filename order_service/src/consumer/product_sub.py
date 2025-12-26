import logging

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from faststream.rabbit.fastapi import RabbitRouter

from src.config import get_settings
from src.core import get_db_session
from src.models import Product
from src.schemas import ProductAddDTO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

router = RabbitRouter(settings.rabbitmq_url)

# Подписчик на события от auth-service
@router.subscriber("product.created")
async def handle_user_created(data: ProductAddDTO, session: AsyncSession = Depends(get_db_session)):
    """Обработка события создания пользователя"""

    logger.info(f"New product is received in order service: {data.name}")
    product = Product(
        name=data.name,
        price=data.price,
        storage_quantity=data.quantity
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)

    # Отправка события в RabbitMQ
    logger.info("Product created successfully!")
