import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ScanResult, BulkScanTask, Blacklist
from app.utils.url_parser import get_url_hash


async def create_scan_result(
    db: AsyncSession,
    url: str,
    is_phishing: bool,
    confidence: float,
    risk_score: int,
    risk_level: str,
    features: Dict[str, Any],
    feature_importance: Dict[str, float],
    scan_duration_ms: int,
    error: Optional[str] = None,
) -> ScanResult:
    result = ScanResult(
        id=str(uuid.uuid4()),
        url=url,
        url_hash=get_url_hash(url),
        is_phishing=is_phishing,
        confidence=confidence,
        risk_score=risk_score,
        risk_level=risk_level,
        features=features,
        feature_importance=feature_importance,
        scan_duration_ms=scan_duration_ms,
        error=error,
        created_at=datetime.now(timezone.utc),
    )
    db.add(result)
    await db.flush()
    await db.refresh(result)
    return result


async def get_scan_result(db: AsyncSession, scan_id: str) -> Optional[ScanResult]:
    stmt = select(ScanResult).where(ScanResult.id == scan_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_scan_by_url_hash(
    db: AsyncSession, url_hash: str
) -> Optional[ScanResult]:
    stmt = (
        select(ScanResult)
        .where(ScanResult.url_hash == url_hash)
        .order_by(ScanResult.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_scan_results(
    db: AsyncSession, skip: int = 0, limit: int = 20
) -> List[ScanResult]:
    stmt = (
        select(ScanResult)
        .order_by(ScanResult.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_scan_stats(db: AsyncSession) -> Dict[str, Any]:
    total = await db.scalar(select(func.count()).select_from(ScanResult))
    phishing = await db.scalar(
        select(func.count()).select_from(ScanResult).where(ScanResult.is_phishing == True)  # noqa: E712
    )
    avg_conf = await db.scalar(select(func.avg(ScanResult.confidence)).select_from(ScanResult))
    total = total or 0
    phishing = phishing or 0
    avg_conf = float(avg_conf or 0.0)
    return {
        "total_scans": total,
        "phishing_count": phishing,
        "clean_count": total - phishing,
        "avg_confidence": round(avg_conf, 4),
        "phishing_rate": round(phishing / total, 4) if total else 0.0,
    }


async def create_bulk_task(db: AsyncSession, total_urls: int) -> BulkScanTask:
    task = BulkScanTask(
        id=str(uuid.uuid4()),
        status="pending",
        total_urls=total_urls,
        processed_urls=0,
        results=[],
        created_at=datetime.now(timezone.utc),
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def get_bulk_task(
    db: AsyncSession, task_id: str
) -> Optional[BulkScanTask]:
    stmt = select(BulkScanTask).where(BulkScanTask.id == task_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_bulk_task(
    db: AsyncSession,
    task: BulkScanTask,
    status: str,
    processed_urls: int,
    results: List[Dict[str, Any]],
    completed_at: Optional[datetime] = None,
) -> BulkScanTask:
    task.status = status
    task.processed_urls = processed_urls
    task.results = results
    if completed_at:
        task.completed_at = completed_at
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def is_domain_blacklisted(db: AsyncSession, domain: str) -> bool:
    stmt = select(Blacklist).where(Blacklist.domain == domain)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None
