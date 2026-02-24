import os
import time
import joblib
import numpy as np
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from app.models.feature_extractor import FeatureExtractor
from app.utils.logger import get_logger

logger = get_logger(__name__)

MODEL_VERSION = "1.0.0"
RISK_LEVELS = {
    (0, 30): "LOW",
    (31, 60): "MEDIUM",
    (61, 85): "HIGH",
    (86, 100): "CRITICAL",
}


def _risk_level(score: int) -> str:
    for (low, high), level in RISK_LEVELS.items():
        if low <= score <= high:
            return level
    return "CRITICAL"


class EnsemblePhishingModel:
    """Loads and runs the ensemble phishing detection model."""

    def __init__(self, model_path: str) -> None:
        self.model_path = model_path
        self.model: Optional[Any] = None
        self.feature_extractor = FeatureExtractor()
        self._loaded = False

    def load(self) -> None:
        """Load model from disk. Trains a demo model if not found."""
        path = Path(self.model_path)
        if path.exists():
            try:
                self.model = joblib.load(str(path))
                self._loaded = True
                logger.info({"msg": "Model loaded", "path": str(path)})
                return
            except Exception as exc:
                logger.warning({"msg": "Failed to load model", "error": str(exc)})

        logger.info({"msg": "No model found – training demo model"})
        self._train_demo_model(path)

    def _train_demo_model(self, path: Path) -> None:
        """Train a lightweight demo model so the app starts without pre-trained file."""
        from sklearn.ensemble import RandomForestClassifier, VotingClassifier
        import xgboost as xgb
        import lightgbm as lgb

        X, y = self._generate_demo_data()

        rf = RandomForestClassifier(n_estimators=50, random_state=42)
        xgb_clf = xgb.XGBClassifier(
            n_estimators=50, use_label_encoder=False,
            eval_metric="logloss", random_state=42, verbosity=0,
        )
        lgb_clf = lgb.LGBMClassifier(n_estimators=50, random_state=42, verbose=-1)

        ensemble = VotingClassifier(
            estimators=[("rf", rf), ("xgb", xgb_clf), ("lgb", lgb_clf)],
            voting="soft",
        )
        ensemble.fit(X, y)

        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(ensemble, str(path))
        self.model = ensemble
        self._loaded = True
        logger.info({"msg": "Demo model trained and saved", "path": str(path)})

    def _generate_demo_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for the demo model."""
        import pandas as pd

        rng = np.random.default_rng(42)
        feature_names = self.feature_extractor._feature_names()
        n = 200
        rows = []
        labels = []

        for _ in range(n // 2):
            # phishing sample
            row = {k: 0 for k in feature_names}
            row["url_length"] = int(rng.integers(80, 200))
            row["num_dots"] = int(rng.integers(4, 10))
            row["num_hyphens"] = int(rng.integers(2, 8))
            row["has_ip_address"] = int(rng.random() > 0.5)
            row["has_https"] = int(rng.random() > 0.7)
            row["suspicious_words"] = 1
            row["num_subdomains"] = int(rng.integers(3, 6))
            row["domain_age_days"] = int(rng.integers(0, 60))
            row["has_valid_ssl"] = int(rng.random() > 0.6)
            rows.append(row)
            labels.append(1)

        for _ in range(n // 2):
            # legitimate sample
            row = {k: 0 for k in feature_names}
            row["url_length"] = int(rng.integers(20, 60))
            row["num_dots"] = int(rng.integers(1, 3))
            row["has_https"] = 1
            row["suspicious_words"] = 0
            row["num_subdomains"] = int(rng.integers(0, 2))
            row["domain_age_days"] = int(rng.integers(300, 3000))
            row["has_valid_ssl"] = 1
            row["ssl_issuer_is_trusted"] = 1
            rows.append(row)
            labels.append(0)

        df = pd.DataFrame(rows, columns=feature_names)
        return df.values, np.array(labels)

    def predict(self, url: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Run prediction and return structured result."""
        start = time.time()

        if not self._loaded or self.model is None:
            raise RuntimeError("Model is not loaded")

        feature_vector = np.array(
            self.feature_extractor.to_feature_vector(features)
        ).reshape(1, -1)

        proba = self.model.predict_proba(feature_vector)[0]
        phishing_prob = float(proba[1])
        risk_score = int(round(phishing_prob * 100))
        is_phishing = phishing_prob >= 0.5
        confidence = phishing_prob if is_phishing else 1.0 - phishing_prob
        level = _risk_level(risk_score)

        # Feature importance (best-effort)
        importance: Dict[str, float] = {}
        try:
            feature_names = self.feature_extractor._feature_names()
            for est_name, estimator in self.model.named_estimators_.items():
                if hasattr(estimator, "feature_importances_"):
                    for fn, fi in zip(feature_names, estimator.feature_importances_):
                        importance[fn] = importance.get(fn, 0.0) + float(fi)
                    break
        except Exception:
            pass

        elapsed_ms = int((time.time() - start) * 1000)

        return {
            "url": url,
            "is_phishing": is_phishing,
            "confidence": round(confidence, 4),
            "risk_score": risk_score,
            "risk_level": level,
            "features": features,
            "feature_importance": importance,
            "model_version": MODEL_VERSION,
            "scan_time_ms": elapsed_ms,
        }

    @property
    def is_loaded(self) -> bool:
        return self._loaded


# Global singleton
_model_instance: Optional[EnsemblePhishingModel] = None


def get_model() -> EnsemblePhishingModel:
    global _model_instance
    if _model_instance is None:
        from app.config import settings
        _model_instance = EnsemblePhishingModel(settings.MODEL_PATH)
    return _model_instance
