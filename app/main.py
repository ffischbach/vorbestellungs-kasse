from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from alembic.config import Config
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from alembic import command
from app.config import settings
from app.routers import admin, orders, sse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(sse.router)
