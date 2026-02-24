#!/usr/bin/env python3
"""Seed database with sample phishing and legitimate URLs."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

PHISHING_URLS = [
    "http://paypa1-secure-login.xyz/update/account",
    "http://192.168.1.100/bank/login.php",
    "http://secure-banking-login.tk/verify?user=1",
    "http://apple-id-suspended.ml/account/verify",
    "http://amazon-prize-winner.ga/claim",
    "http://microsoft-support-alert.cf/scan",
    "http://netflix-billing-update.tk/payment",
    "http://g00gle-security.xyz/alert",
    "http://faceb00k-login.ml/account",
    "http://wellsfarg0-online.tk/signin",
] * 50  # ~500 phishing URLs

LEGIT_URLS = [
    "https://google.com",
    "https://github.com",
    "https://stackoverflow.com",
    "https://python.org",
    "https://fastapi.tiangolo.com",
    "https://reactjs.org",
    "https://tailwindcss.com",
    "https://postgresql.org",
    "https://redis.io",
    "https://docker.com",
] * 50  # ~500 legit URLs

BLACKLIST_DOMAINS = [
    "paypa1-secure-login.xyz",
    "secure-banking-login.tk",
    "apple-id-suspended.ml",
    "amazon-prize-winner.ga",
    "microsoft-support-alert.cf",
]


async def seed() -> None:
    from app.database.connection import AsyncSessionLocal, init_db
    from app.database.models import ScanResult, Blacklist
    from app.utils.url_parser import get_url_hash
    import uuid
    from datetime import datetime, timezone

    await init_db()

    async with AsyncSessionLocal() as db:
        # Seed blacklist
        for domain in BLACKLIST_DOMAINS:
            entry = Blacklist(domain=domain, source="seed_data", added_at=datetime.now(timezone.utc))
            db.add(entry)
        await db.commit()
        print(f"Seeded {len(BLACKLIST_DOMAINS)} blacklist entries")


if __name__ == "__main__":
    asyncio.run(seed())
