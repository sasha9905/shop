from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src import db_dependency_instance, router
from src.core.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    try:
        await db_dependency_instance.table_creating()
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}", exc_info=True)
        raise
    yield
    logger.info("Shutting down application...")


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)

