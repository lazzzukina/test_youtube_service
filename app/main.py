import structlog
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlmodel import SQLModel

from app.database import engine
from app.middleware import setup_middleware
from app.routers.fetch import router as fetch_router
from app.routers.videos import router as videos_router
from app.routers.webhook import router as webhook_router

# structured logging
structlog.configure(processors=[structlog.processors.JSONRenderer()])
app = FastAPI(title="YouTube processing service")

# middleware
setup_middleware(app)

# include routers
app.include_router(fetch_router)
app.include_router(videos_router)
app.include_router(webhook_router)

# metrics
Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
