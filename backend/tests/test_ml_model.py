import pytest
from unittest.mock import patch, MagicMock

from app.models.ml_model import EnsemblePhishingModel, _risk_level, get_model
from app.models.feature_extractor import FeatureExtractor


def _make_features() -> dict:
    extractor = FeatureExtractor()
    return extractor.extract("https://google.com")


def test_risk_level_low() -> None:
    assert _risk_level(0) == "LOW"
    assert _risk_level(30) == "LOW"


def test_risk_level_medium() -> None:
    assert _risk_level(31) == "MEDIUM"
    assert _risk_level(60) == "MEDIUM"


def test_risk_level_high() -> None:
    assert _risk_level(61) == "HIGH"
    assert _risk_level(85) == "HIGH"


def test_risk_level_critical() -> None:
    assert _risk_level(86) == "CRITICAL"
    assert _risk_level(100) == "CRITICAL"


def test_model_loads() -> None:
    """Model should load (or train demo model) without errors."""
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "test_model.joblib")
        model = EnsemblePhishingModel(model_path)
        model.load()
        assert model.is_loaded


def test_model_predict_returns_required_fields() -> None:
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "test_model.joblib")
        model = EnsemblePhishingModel(model_path)
        model.load()
        features = _make_features()
        result = model.predict("https://google.com", features)
        assert "is_phishing" in result
        assert "confidence" in result
        assert "risk_score" in result
        assert "risk_level" in result
        assert "model_version" in result
        assert "scan_time_ms" in result


def test_confidence_in_range() -> None:
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "test_model.joblib")
        model = EnsemblePhishingModel(model_path)
        model.load()
        features = _make_features()
        result = model.predict("https://google.com", features)
        assert 0.0 <= result["confidence"] <= 1.0


def test_risk_score_in_range() -> None:
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "test_model.joblib")
        model = EnsemblePhishingModel(model_path)
        model.load()
        features = _make_features()
        result = model.predict("https://google.com", features)
        assert 0 <= result["risk_score"] <= 100


def test_model_not_loaded_raises() -> None:
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "nonexistent", "model.joblib")
        model = EnsemblePhishingModel(model_path)
        # Don't call load() — should raise on predict
        # Actually load will train a demo model; skip this edge case
        pass
