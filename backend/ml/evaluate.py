"""
Evaluation script – loads a trained model and evaluates it on a test set.
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.train import generate_dataset, FEATURE_NAMES  # noqa: E402


def evaluate(model_path: str = "models/ensemble_model.joblib") -> None:
    path = Path(__file__).parent / model_path
    if not path.exists():
        print(f"Model not found at {path}. Run train.py first.")
        return

    model = joblib.load(str(path))
    df = generate_dataset(200, 200)
    X = df[FEATURE_NAMES].values
    y = df["label"].values

    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1]

    print(f"Accuracy: {accuracy_score(y, y_pred):.4f}")
    print(f"ROC-AUC:  {roc_auc_score(y, y_proba):.4f}")
    print(classification_report(y, y_pred))


if __name__ == "__main__":
    evaluate()
