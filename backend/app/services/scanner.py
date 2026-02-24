import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feature_extractor import FeatureExtractor
from app.models.ml_model import get_model
from app.services.html_analyzer import analyze_html
from app.services.ssl_service import check_ssl
from app.services.whois_service import get_whois_info
from app.services.blacklist_service import check_blacklist
from app.services.cache_service import cache_get, cache_set
from app.database.crud import create_scan_result
from app.utils.url_parser import (
    normalize_url,
    is_valid_url,
    extract_domain,
    extract_hostname,
    get_url_hash,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Scanner:
    def __init__(self) -> None:
        self.feature_extractor = FeatureExtractor()

    async def scan(
        self, url: str, db: AsyncSession, use_cache: bool = True
    ) -> Dict[str, Any]:
        """Full scan pipeline: normalize → features → ML → save → return."""
        start = time.time()

        # Normalize URL
        try:
            url = normalize_url(url)
        except Exception:
            pass

        if not is_valid_url(url):
            return self._error_result(url, "Invalid URL format")

        # Cache check
        url_hash = get_url_hash(url)
        cache_key = f"scan:{url_hash}"
        if use_cache:
            cached = await cache_get(cache_key)
            if cached:
                logger.info({"msg": "Cache hit", "url": url})
                return cached

        # Feature extraction
        features = self.feature_extractor.extract(url)

        # Enrich with service data
        hostname = extract_hostname(url)
        domain = extract_domain(url)

        # SSL (synchronous – run in thread if needed)
        try:
            ssl_features = check_ssl(hostname)
            features.update(ssl_features)
        except Exception as exc:
            logger.debug({"msg": "SSL check skipped", "error": str(exc)})

        # WHOIS
        try:
            whois_features = get_whois_info(domain)
            features.update(whois_features)
        except Exception as exc:
            logger.debug({"msg": "WHOIS skipped", "error": str(exc)})

        # Blacklist
        try:
            features["is_blacklisted"] = await check_blacklist(url, db)
        except Exception as exc:
            logger.debug({"msg": "Blacklist check skipped", "error": str(exc)})

        # HTML analysis
        try:
            html_features = await analyze_html(url)
            features.update(html_features)
        except Exception as exc:
            logger.debug({"msg": "HTML analysis skipped", "error": str(exc)})

        # ML prediction
        model = get_model()
        prediction = model.predict(url, features)
        elapsed_ms = int((time.time() - start) * 1000)
        prediction["scan_time_ms"] = elapsed_ms

        # Persist to DB
        try:
            record = await create_scan_result(
                db=db,
                url=url,
                is_phishing=prediction["is_phishing"],
                confidence=prediction["confidence"],
                risk_score=prediction["risk_score"],
                risk_level=prediction["risk_level"],
                features=features,
                feature_importance=prediction.get("feature_importance", {}),
                scan_duration_ms=elapsed_ms,
            )
            prediction["id"] = str(record.id)
            prediction["created_at"] = record.created_at.isoformat()
        except Exception as exc:
            logger.error({"msg": "DB save failed", "error": str(exc)})
            prediction["id"] = ""
            prediction["created_at"] = datetime.now(timezone.utc).isoformat()

        # Cache result
        try:
            await cache_set(cache_key, prediction)
        except Exception:
            pass

        return prediction

    def _error_result(self, url: str, error: str) -> Dict[str, Any]:
        return {
            "id": "",
            "url": url,
            "is_phishing": False,
            "confidence": 0.0,
            "risk_score": 0,
            "risk_level": "LOW",
            "features": {},
            "feature_importance": {},
            "model_version": "1.0.0",
            "scan_time_ms": 0,
            "error": error,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


_scanner_instance: Optional[Scanner] = None


def get_scanner() -> Scanner:
    global _scanner_instance
    if _scanner_instance is None:
        _scanner_instance = Scanner()
    return _scanner_instance
