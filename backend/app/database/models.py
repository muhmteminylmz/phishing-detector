import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Float, Integer, String, Text, DateTime, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class ScanResult(Base):
    __tablename__ = "scan_results"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    url_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    is_phishing: Mapped[bool] = mapped_column(Boolean, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    features: Mapped[dict] = mapped_column(JSON, nullable=True)
    feature_importance: Mapped[dict] = mapped_column(JSON, nullable=True)
    scan_duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class BulkScanTask(Base):
    __tablename__ = "bulk_scan_tasks"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    total_urls: Mapped[int] = mapped_column(Integer, nullable=False)
    processed_urls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    results: Mapped[list] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Blacklist(Base):
    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
