import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker
from src.config import get_settings
from src.core.security import decode_token

logger = logging.getLogger(__name__)
settings = get_settings()
broker = RabbitBroker(settings.rabbitmq_url)
app = FastStream(broker)

async def publish_event(event_type: str, data: dict):
    try:
        await broker.publish(
            {
                "event": event_type,
                "data": data,
                "timestamp": "2024-01-01T00:00:00"
            },
            routing_key=f"auth.{event_type}"  # routing_key = имя очереди
        )
        print(f"Event published: {event_type}")
    except Exception as e:
        print(f"Failed to publish event: {e}")

@broker.subscriber("auth.verify_token")
async def verify_token_handler(
    token: str
) -> dict:
    """Валидация токена для других сервисов"""
    try:
        payload = decode_token(token)
        if payload:
            return {
                "valid": True,
                "user_id": payload.sub,
                "role": payload.role
            }
        return {"valid": False, "error": "Invalid token"}
    except Exception as e:
        logger.error(f"Token verification error: {e}", exc_info=True)
        return {"valid": False, "error": str(e)}

# Запуск консьюмера в фоне
async def start_event_consumer():
    await app.run()
