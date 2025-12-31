from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src import db_dependency_instance, router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    await db_dependency_instance.table_creating()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8001)
