from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api import router as api_router
from db_dependency import db_dependency


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    await db_dependency.table_creating()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app")

