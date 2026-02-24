from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_whois_info(domain: str) -> Dict[str, Any]:
    """Query WHOIS for domain information."""
    result: Dict[str, Any] = {
        "domain_age_days": -1,
        "domain_registration_length": -1,
    }
    if not domain:
        return result
    try:
        import whois  # type: ignore
        w = whois.whois(domain)
        creation_date = w.creation_date
        expiration_date = w.expiration_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        now = datetime.now(timezone.utc)

        if creation_date:
            if creation_date.tzinfo is None:
                creation_date = creation_date.replace(tzinfo=timezone.utc)
            result["domain_age_days"] = max(0, (now - creation_date).days)

        if creation_date and expiration_date:
            if expiration_date.tzinfo is None:
                expiration_date = expiration_date.replace(tzinfo=timezone.utc)
            result["domain_registration_length"] = max(
                0, (expiration_date - creation_date).days
            )
    except Exception as exc:
        logger.debug({"msg": "WHOIS failed", "domain": domain, "error": str(exc)})
    return result
