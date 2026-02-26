"""
Export the trained ensemble model's Random Forest trees to a JSON file
that can be loaded in the browser for client-side inference.

Usage:
    cd backend
    python ../scripts/export_model_json.py

Output:
    frontend/public/model.json
"""
import json
import sys
from pathlib import Path

import numpy as np

# Allow importing from backend
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.models.feature_extractor import FeatureExtractor
from app.models.ml_model import EnsemblePhishingModel


def export_rf_trees(model) -> list:
    """Extract decision trees from the Random Forest estimator."""
    # The ensemble is a VotingClassifier; grab the RF from it
    rf = model.named_estimators_["rf"]
    trees = []
    for estimator in rf.estimators_:
        tree = estimator.tree_
        trees.append({
            "children_left": tree.children_left.tolist(),
            "children_right": tree.children_right.tolist(),
            "feature": tree.feature.tolist(),
            "threshold": [round(float(t), 6) for t in tree.threshold],
            "value": [[round(float(v), 6) for v in node[0]] for node in tree.value],
        })
    return trees


def main():
    root = Path(__file__).parent.parent
    frontend_public = root / "frontend" / "public"
    frontend_public.mkdir(parents=True, exist_ok=True)

    extractor = FeatureExtractor()
    feature_names = extractor._feature_names()

    # Train a demo model (same as what the app uses at startup)
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "export_model.joblib")
        model = EnsemblePhishingModel(model_path)
        model.load()  # trains demo model

        ensemble = model.model
        rf_trees = export_rf_trees(ensemble)

        # Also export feature importance from the RF
        rf = ensemble.named_estimators_["rf"]
        importance = {}
        for name, imp in zip(feature_names, rf.feature_importances_):
            importance[name] = round(float(imp), 6)

        payload = {
            "version": "1.0.0",
            "feature_names": feature_names,
            "n_features": len(feature_names),
            "n_trees": len(rf_trees),
            "trees": rf_trees,
            "feature_importance": importance,
        }

        out_path = frontend_public / "model.json"
        with open(out_path, "w") as f:
            json.dump(payload, f)

        size_kb = out_path.stat().st_size / 1024
        print(f"✅ Model exported to {out_path} ({size_kb:.1f} KB)")
        print(f"   Trees: {len(rf_trees)}, Features: {len(feature_names)}")


if __name__ == "__main__":
    main()
