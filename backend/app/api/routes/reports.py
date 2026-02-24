from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.crud import get_scan_stats
from app.models.schemas import StatsResponse

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)) -> StatsResponse:
    """Return aggregate statistics about all scans."""
    stats = await get_scan_stats(db)
    return StatsResponse(**stats)
