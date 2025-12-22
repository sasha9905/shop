import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src import db_dependency_instance, router
from src.core import broker, start_event_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    await db_dependency_instance.table_creating()
    task = asyncio.create_task(start_event_consumer())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)

