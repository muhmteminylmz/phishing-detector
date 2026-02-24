import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone

from app.main import app


def _mock_scan_result(url: str = "https://google.com") -> dict:
    return {
        "id": "test-scan-id",
        "url": url,
        "is_phishing": False,
        "confidence": 0.9,
        "risk_score": 10,
        "risk_level": "LOW",
        "features": {"url_length": 18},
        "feature_importance": {"url_length": 0.1},
        "model_version": "1.0.0",
        "scan_time_ms": 100,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.mark.asyncio
async def test_health_check() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data


@pytest.mark.asyncio
async def test_scan_invalid_url() -> None:
    with patch("app.api.routes.scan.get_scanner") as mock_get_scanner:
        scanner = MagicMock()
        scanner.scan = AsyncMock(return_value={
            "id": "",
            "url": "not-a-valid-url!!!",
            "is_phishing": False,
            "confidence": 0.0,
            "risk_score": 0,
            "risk_level": "LOW",
            "features": {},
            "feature_importance": {},
            "model_version": "1.0.0",
            "scan_time_ms": 0,
            "error": "Invalid URL format",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        mock_get_scanner.return_value = scanner

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/scan/url", json={"url": "not-a-valid-url!!!"}
            )
    assert response.status_code in (200, 422)


@pytest.mark.asyncio
async def test_scan_valid_url() -> None:
    with patch("app.api.routes.scan.get_scanner") as mock_get_scanner:
        scanner = MagicMock()
        scanner.scan = AsyncMock(return_value=_mock_scan_result("https://google.com"))
        mock_get_scanner.return_value = scanner

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/scan/url", json={"url": "https://google.com"}
            )
    assert response.status_code == 200
    data = response.json()
    assert "is_phishing" in data
    assert "risk_score" in data
    assert 0 <= data["risk_score"] <= 100


@pytest.mark.asyncio
async def test_scan_phishing_url() -> None:
    suspicious = "http://paypa1-secure-login.xyz/update/account?verify=1"
    phishing_result = _mock_scan_result(suspicious)
    phishing_result.update({"is_phishing": True, "risk_score": 94, "risk_level": "CRITICAL", "confidence": 0.94})

    with patch("app.api.routes.scan.get_scanner") as mock_get_scanner:
        scanner = MagicMock()
        scanner.scan = AsyncMock(return_value=phishing_result)
        mock_get_scanner.return_value = scanner

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/scan/url", json={"url": suspicious}
            )
    assert response.status_code == 200
    data = response.json()
    assert "is_phishing" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_bulk_scan() -> None:
    urls = [
        "https://google.com",
        "https://github.com",
        "http://paypa1-secure.xyz/login",
    ]

    mock_task = MagicMock()
    mock_task.id = "bulk-task-id"

    with (
        patch("app.api.routes.scan.create_bulk_task", new_callable=AsyncMock, return_value=mock_task),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/scan/bulk", json={"urls": urls})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["total_urls"] == 3


@pytest.mark.asyncio
async def test_root() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
    assert response.status_code == 200

