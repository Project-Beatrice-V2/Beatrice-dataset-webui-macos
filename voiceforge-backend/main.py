"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import get_settings
from database import init_db
from api.routes_jobs import router as jobs_router
from api.routes_convert import router as convert_router
from api.routes_search import router as search_router
from api.routes_history import router as history_router
from api.websocket import router as ws_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    settings.ensure_dirs()
    logger.info("VoiceForge Dataset Studio started")
    yield
    logger.info("VoiceForge shutting down")


app = FastAPI(
    title="VoiceForge Dataset Studio",
    description="AI Voice Dataset Creator — search, extract, and package voice datasets",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.include_router(convert_router)
app.include_router(search_router)
app.include_router(history_router)
app.include_router(ws_router)

app.mount("/static", StaticFiles(directory=str(settings.BASE_DIR / "static")), name="static")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "voiceforge", "version": "1.0.0"}


@app.get("/api/health")
def api_health():
    return {"status": "ok", "redis": _check_redis()}


def _check_redis() -> str:
    try:
        from workers.celery_app import redis_client

        redis_client.ping()
        return "connected"
    except Exception:
        return "disconnected"
