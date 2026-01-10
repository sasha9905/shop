import httpx

from src.core.logging_config import logger


async def verify_token_with_auth_service(token: str) -> dict:
    """
    Проверка токена через HTTP запрос к auth-service
    
    Args:
        token: Токен для проверки
        
    Returns:
        Словарь с результатом проверки токена
    """
    async with httpx.AsyncClient() as client:
        try:
            logger.info("Token received, sending to auth service for verification")
            response = await client.post(
                "http://localhost:8000/api/v1/auth/verify",
                params={"token": token}
            )
            logger.info("Response received from auth service")
            return response.json()
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}", exc_info=True)
            return {"valid": False}

