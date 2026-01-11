from src.core.logging_config import logger
import httpx

async def verify_token_with_auth_service(token: str) -> dict:
    """Проверка токена через HTTP запрос к auth-service"""
    async with httpx.AsyncClient() as client:
        try:
            logger.info("Token is received and sent to auth service.")
            response = await client.post(
                "http://auth_service:8000/api/v1/auth/verify",
                params={"token": token}
            )
            logger.info(f"Response is received.")
            return response.json()
        except:
            return {"valid": False}

