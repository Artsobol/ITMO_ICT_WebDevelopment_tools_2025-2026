from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from core.config import settings
from api import router as api_router
from core.models import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        await db_helper.dispose()


mainapp = FastAPI(
    lifespan=lifespan,
)
mainapp.include_router(api_router, prefix=settings.api.prefix)


@mainapp.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:mainapp", host=settings.run.host, port=settings.run.port, reload=True
    )
