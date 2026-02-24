"""
Shared pytest configuration and fixtures.
"""
import pytest
import tempfile
import os

from app.models.ml_model import get_model, _model_instance
import app.models.ml_model as ml_module


@pytest.fixture(scope="session", autouse=True)
def load_model_for_tests():
    """Ensure the ML model is loaded once for all tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "test_model.joblib")
        model = get_model()
        # Override path and load (trains demo model)
        model.model_path = model_path
        model.load()
        yield
        # Reset singleton for cleanliness
        ml_module._model_instance = None
