"""Tests for model persistence — pre-trained model copy and load."""
import os
import tempfile
from pathlib import Path

import joblib
import numpy as np
import pytest

from app.models.ml_model import EnsemblePhishingModel


def test_model_loads_from_existing_file() -> None:
    """When a pre-trained model file exists, it should be loaded directly
    without triggering demo training."""
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "ensemble_model.joblib")

        # First: create and save a model
        model1 = EnsemblePhishingModel(model_path)
        model1.load()  # trains demo model
        assert model1.is_loaded
        assert os.path.exists(model_path)
        mtime_after_first = os.path.getmtime(model_path)

        # Second: load from the saved file — no retraining should happen
        model2 = EnsemblePhishingModel(model_path)
        model2.load()
        assert model2.is_loaded
        # The file should not have been overwritten
        mtime_after_second = os.path.getmtime(model_path)
        assert mtime_after_first == mtime_after_second


def test_model_survives_reload() -> None:
    """Model produces consistent predictions across save/load cycles."""
    from app.models.feature_extractor import FeatureExtractor

    extractor = FeatureExtractor()
    features = extractor.extract("https://google.com")

    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "model.joblib")

        # Train, predict, save
        model1 = EnsemblePhishingModel(model_path)
        model1.load()
        result1 = model1.predict("https://google.com", features)

        # Load from file, predict again
        model2 = EnsemblePhishingModel(model_path)
        model2.load()
        result2 = model2.predict("https://google.com", features)

        # Results should be identical
        assert result1["is_phishing"] == result2["is_phishing"]
        assert result1["risk_score"] == result2["risk_score"]
        assert result1["confidence"] == result2["confidence"]
