from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db, check_db_connection
from app.services.cache_service import check_redis_connection
from app.models.ml_model import get_model
from app.models.schemas import HealthResponse

router = APIRouter(prefix="/api/v1/health", tags=["health"])

APP_VERSION = "1.0.0"


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()
    model = get_model()
    return HealthResponse(
        status="ok" if db_ok else "degraded",
        version=APP_VERSION,
        model_loaded=model.is_loaded,
        database="connected" if db_ok else "error",
        redis="connected" if redis_ok else "error",
    )
