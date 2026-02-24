from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ScanRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def url_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        return v


class BulkScanRequest(BaseModel):
    urls: List[str]

    @field_validator("urls")
    @classmethod
    def urls_must_not_be_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("URL list cannot be empty")
        if len(v) > 100:
            raise ValueError("Cannot scan more than 100 URLs at once")
        return v


class ScanResultResponse(BaseModel):
    id: str
    url: str
    is_phishing: bool
    confidence: float
    risk_score: int
    risk_level: str
    features: Dict[str, Any]
    feature_importance: Dict[str, float]
    model_version: str
    scan_time_ms: int
    error: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class BulkScanResponse(BaseModel):
    task_id: str
    status: str
    total_urls: int
    message: str


class BulkScanStatusResponse(BaseModel):
    task_id: str
    status: str
    total_urls: int
    processed_urls: int
    results: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    database: str
    redis: str

    model_config = {"protected_namespaces": ()}


class StatsResponse(BaseModel):
    total_scans: int
    phishing_count: int
    clean_count: int
    avg_confidence: float
    phishing_rate: float
