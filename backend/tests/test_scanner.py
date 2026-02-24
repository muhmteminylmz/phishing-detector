import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.services.scanner import Scanner


@pytest.mark.asyncio
async def test_scanner_invalid_url() -> None:
    scanner = Scanner()
    db = AsyncMock()
    result = await scanner.scan("not-a-url!!!", db, use_cache=False)
    assert isinstance(result, dict)
    assert "url" in result
    # After normalization, the scanner may or may not return an error
    # but it must always return a dict with the expected keys
    assert "is_phishing" in result or "error" in result


@pytest.mark.asyncio
async def test_scanner_returns_required_keys() -> None:
    scanner = Scanner()
    db = AsyncMock()

    mock_record = MagicMock()
    mock_record.id = "test-id"
    mock_record.created_at = datetime.now(timezone.utc)

    with (
        patch("app.services.scanner.check_ssl", return_value={}),
        patch("app.services.scanner.get_whois_info", return_value={}),
        patch("app.services.scanner.check_blacklist", new_callable=AsyncMock, return_value=0),
        patch("app.services.scanner.analyze_html", new_callable=AsyncMock, return_value={}),
        patch("app.services.scanner.create_scan_result", new_callable=AsyncMock, return_value=mock_record),
    ):
        result = await scanner.scan("https://google.com", db, use_cache=False)

    required_keys = {"url", "is_phishing", "confidence", "risk_score", "risk_level"}
    assert required_keys.issubset(result.keys())
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0 <= result["risk_score"] <= 100
