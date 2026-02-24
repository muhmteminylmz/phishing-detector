import asyncio
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.crud import (
    get_scan_result,
    list_scan_results,
    get_bulk_task,
    create_bulk_task,
    update_bulk_task,
)
from app.models.schemas import (
    ScanRequest,
    BulkScanRequest,
    ScanResultResponse,
    BulkScanResponse,
    BulkScanStatusResponse,
)
from app.services.scanner import get_scanner
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/scan", tags=["scan"])


@router.post("/url", response_model=ScanResultResponse)
async def scan_url(
    request: ScanRequest,
    db: AsyncSession = Depends(get_db),
) -> ScanResultResponse:
    """Scan a single URL for phishing."""
    scanner = get_scanner()
    result = await scanner.scan(request.url, db)
    if result.get("error") and not result.get("id"):
        raise HTTPException(status_code=422, detail=result["error"])
    return ScanResultResponse(
        id=result["id"] or "unknown",
        url=result["url"],
        is_phishing=result["is_phishing"],
        confidence=result["confidence"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        features=result["features"],
        feature_importance=result["feature_importance"],
        model_version=result["model_version"],
        scan_time_ms=result["scan_time_ms"],
        error=result.get("error"),
        created_at=datetime.fromisoformat(result["created_at"])
        if isinstance(result["created_at"], str)
        else result["created_at"],
    )


@router.post("/bulk", response_model=BulkScanResponse)
async def bulk_scan(
    request: BulkScanRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> BulkScanResponse:
    """Start a bulk URL scan. Returns task_id for status polling."""
    from app.database.connection import AsyncSessionLocal

    task = await create_bulk_task(db, total_urls=len(request.urls))
    task_id = str(task.id)
    await db.commit()

    async def _run_bulk(urls: List[str], tid: str) -> None:
        async with AsyncSessionLocal() as session:
            scanner = get_scanner()
            results = []
            bulk_task = await get_bulk_task(session, tid)
            if bulk_task is None:
                return
            bulk_task.status = "running"
            session.add(bulk_task)
            await session.commit()

            for i, url in enumerate(urls):
                try:
                    r = await scanner.scan(url, session)
                except Exception as exc:
                    r = {"url": url, "error": str(exc)}
                results.append(r)
                bulk_task = await get_bulk_task(session, tid)
                if bulk_task:
                    await update_bulk_task(
                        session, bulk_task, "running", i + 1, results
                    )
                    await session.commit()

            bulk_task = await get_bulk_task(session, tid)
            if bulk_task:
                await update_bulk_task(
                    session, bulk_task, "completed",
                    len(urls), results,
                    completed_at=datetime.now(timezone.utc),
                )
                await session.commit()

    background_tasks.add_task(_run_bulk, request.urls, task_id)
    return BulkScanResponse(
        task_id=task_id,
        status="pending",
        total_urls=len(request.urls),
        message="Bulk scan started. Poll /bulk/{task_id} for status.",
    )


@router.get("/bulk/{task_id}", response_model=BulkScanStatusResponse)
async def bulk_scan_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> BulkScanStatusResponse:
    """Get status of a bulk scan task."""
    task = await get_bulk_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return BulkScanStatusResponse(
        task_id=str(task.id),
        status=task.status,
        total_urls=task.total_urls,
        processed_urls=task.processed_urls,
        results=task.results,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )


@router.get("/history", response_model=List[ScanResultResponse])
async def scan_history(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> List[ScanResultResponse]:
    """Return paginated scan history."""
    if limit > 100:
        limit = 100
    records = await list_scan_results(db, skip=skip, limit=limit)
    return [
        ScanResultResponse(
            id=str(r.id),
            url=r.url,
            is_phishing=r.is_phishing,
            confidence=r.confidence,
            risk_score=r.risk_score,
            risk_level=r.risk_level,
            features=r.features or {},
            feature_importance=r.feature_importance or {},
            model_version="1.0.0",
            scan_time_ms=r.scan_duration_ms or 0,
            error=r.error,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/{scan_id}", response_model=ScanResultResponse)
async def get_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
) -> ScanResultResponse:
    """Retrieve a specific scan result by ID."""
    record = await get_scan_result(db, scan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanResultResponse(
        id=str(record.id),
        url=record.url,
        is_phishing=record.is_phishing,
        confidence=record.confidence,
        risk_score=record.risk_score,
        risk_level=record.risk_level,
        features=record.features or {},
        feature_importance=record.feature_importance or {},
        model_version="1.0.0",
        scan_time_ms=record.scan_duration_ms or 0,
        error=record.error,
        created_at=record.created_at,
    )
