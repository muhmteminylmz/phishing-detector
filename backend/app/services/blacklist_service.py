from typing import Set
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud import is_domain_blacklisted
from app.utils.url_parser import extract_domain
from app.utils.logger import get_logger

logger = get_logger(__name__)

# In-memory set for fast lookup (populated from DB on startup)
_BLACKLIST_CACHE: Set[str] = set()


def preload_blacklist(domains: Set[str]) -> None:
    """Populate in-memory cache."""
    global _BLACKLIST_CACHE
    _BLACKLIST_CACHE = set(d.lower() for d in domains)
    logger.info({"msg": "Blacklist cache loaded", "count": len(_BLACKLIST_CACHE)})


async def check_blacklist(url: str, db: AsyncSession) -> int:
    """Return 1 if the URL's domain is blacklisted, 0 otherwise."""
    domain = extract_domain(url).lower()
    if not domain:
        return 0
    if domain in _BLACKLIST_CACHE:
        return 1
    # Fall back to DB
    try:
        if await is_domain_blacklisted(db, domain):
            _BLACKLIST_CACHE.add(domain)
            return 1
    except Exception as exc:
        logger.debug({"msg": "Blacklist DB check failed", "error": str(exc)})
    return 0
