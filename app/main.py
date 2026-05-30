from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine
from app.routers import admin, orders, sse


def _migrate(conn: object) -> None:
    """Add columns introduced after initial deployment (SQLite-safe ALTER TABLE)."""
    migrations = [
        "ALTER TABLE orders ADD COLUMN handed_out BOOLEAN NOT NULL DEFAULT 0",
        "ALTER TABLE orders ADD COLUMN handed_out_at DATETIME",
    ]
    for sql in migrations:
        try:
            conn.execute(text(sql))  # type: ignore[attr-defined]
        except Exception:
            pass  # column already exists → ignore


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        _migrate(conn)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(sse.router)
