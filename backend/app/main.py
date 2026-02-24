from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import scan, reports, health
from app.api.middleware import LoggingMiddleware
from app.config import settings
from app.database.connection import init_db, check_db_connection
from app.models.ml_model import get_model
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    logger.info({"msg": "Starting phishing-detector backend"})
    try:
        await init_db()
    except Exception as exc:
        logger.warning({"msg": "DB init failed (may not be available)", "error": str(exc)})

    model = get_model()
    try:
        model.load()
    except Exception as exc:
        logger.warning({"msg": "Model load failed", "error": str(exc)})

    yield

    # Shutdown
    logger.info({"msg": "Shutting down"})


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Phishing Detector API",
    description="ML-based phishing site detection system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Routers
app.include_router(scan.router)
app.include_router(reports.router)
app.include_router(health.router)


@app.get("/")
async def root() -> dict:
    return {"message": "Phishing Detector API", "docs": "/docs"}
