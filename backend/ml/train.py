"""
Training script for the ensemble phishing detection model.
Generates a realistic synthetic dataset, trains an ensemble model,
evaluates it, and saves the result to ml/models/.
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from tqdm import tqdm
import xgboost as xgb
import lightgbm as lgb
import joblib

# Allow importing from backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.feature_extractor import FeatureExtractor  # noqa: E402

RESULTS_DIR = Path(__file__).parent / "results"
MODELS_DIR = Path(__file__).parent / "models"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_EXTRACTOR = FeatureExtractor()
FEATURE_NAMES = FEATURE_EXTRACTOR._feature_names()


def _make_phishing_sample(rng: np.random.Generator) -> dict:
    s = {k: 0 for k in FEATURE_NAMES}
    s["url_length"] = int(rng.integers(80, 250))
    s["hostname_length"] = int(rng.integers(30, 80))
    s["path_length"] = int(rng.integers(20, 100))
    s["num_dots"] = int(rng.integers(4, 12))
    s["num_hyphens"] = int(rng.integers(2, 10))
    s["num_underscores"] = int(rng.integers(0, 5))
    s["num_slashes"] = int(rng.integers(4, 15))
    s["num_at_symbols"] = int(rng.integers(0, 3))
    s["has_ip_address"] = int(rng.random() > 0.6)
    s["has_https"] = int(rng.random() > 0.5)
    s["https_in_hostname"] = int(rng.random() > 0.7)
    s["has_port"] = int(rng.random() > 0.7)
    s["path_entropy"] = round(float(rng.uniform(3.0, 5.0)), 4)
    s["special_char_ratio"] = round(float(rng.uniform(0.15, 0.45)), 4)
    s["digit_ratio"] = round(float(rng.uniform(0.05, 0.25)), 4)
    s["is_shortened"] = int(rng.random() > 0.8)
    s["suspicious_words"] = int(rng.random() > 0.2)
    s["brand_impersonation"] = int(rng.random() > 0.5)
    s["num_subdomains"] = int(rng.integers(2, 7))
    s["num_digits_in_domain"] = int(rng.integers(2, 8))
    s["domain_age_days"] = int(rng.integers(0, 90))
    s["domain_registration_length"] = int(rng.integers(30, 365))
    s["has_valid_ssl"] = int(rng.random() > 0.5)
    s["ssl_issuer_is_trusted"] = int(rng.random() > 0.7)
    s["ssl_days_remaining"] = int(rng.integers(0, 90))
    s["is_blacklisted"] = int(rng.random() > 0.7)
    s["html_form_count"] = int(rng.integers(1, 5))
    s["external_link_ratio"] = round(float(rng.uniform(0.3, 0.9)), 4)
    s["null_hyperlinks"] = int(rng.integers(1, 10))
    s["iframe_count"] = int(rng.integers(0, 5))
    s["javascript_obfuscated"] = int(rng.random() > 0.4)
    s["favicon_from_external"] = int(rng.random() > 0.5)
    s["meta_refresh"] = int(rng.random() > 0.5)
    s["right_click_disabled"] = int(rng.random() > 0.5)
    s["redirection_count"] = int(rng.integers(1, 5))
    s["url_depth"] = int(rng.integers(3, 10))
    return s


def _make_legit_sample(rng: np.random.Generator) -> dict:
    s = {k: 0 for k in FEATURE_NAMES}
    s["url_length"] = int(rng.integers(15, 60))
    s["hostname_length"] = int(rng.integers(8, 25))
    s["path_length"] = int(rng.integers(0, 30))
    s["num_dots"] = int(rng.integers(1, 3))
    s["num_hyphens"] = int(rng.integers(0, 2))
    s["num_slashes"] = int(rng.integers(1, 4))
    s["has_ip_address"] = 0
    s["has_https"] = 1
    s["https_in_hostname"] = 0
    s["has_port"] = 0
    s["path_entropy"] = round(float(rng.uniform(0.5, 2.5)), 4)
    s["special_char_ratio"] = round(float(rng.uniform(0.02, 0.12)), 4)
    s["digit_ratio"] = round(float(rng.uniform(0.0, 0.05)), 4)
    s["is_shortened"] = 0
    s["suspicious_words"] = 0
    s["brand_impersonation"] = 0
    s["num_subdomains"] = int(rng.integers(0, 2))
    s["num_digits_in_domain"] = 0
    s["domain_age_days"] = int(rng.integers(500, 5000))
    s["domain_registration_length"] = int(rng.integers(365, 3650))
    s["has_valid_ssl"] = 1
    s["ssl_issuer_is_trusted"] = 1
    s["ssl_days_remaining"] = int(rng.integers(60, 365))
    s["is_blacklisted"] = 0
    s["html_form_count"] = int(rng.integers(0, 2))
    s["external_link_ratio"] = round(float(rng.uniform(0.0, 0.2)), 4)
    s["null_hyperlinks"] = 0
    s["iframe_count"] = 0
    s["javascript_obfuscated"] = 0
    s["favicon_from_external"] = 0
    s["meta_refresh"] = 0
    s["right_click_disabled"] = 0
    s["redirection_count"] = 0
    s["url_depth"] = int(rng.integers(0, 3))
    return s


def generate_dataset(n_phishing: int = 1000, n_legit: int = 1000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    rows = []
    labels = []
    for _ in tqdm(range(n_phishing), desc="  Phishing samples", unit="sample"):
        rows.append(_make_phishing_sample(rng))
        labels.append(1)
    for _ in tqdm(range(n_legit), desc="  Legit samples   ", unit="sample"):
        rows.append(_make_legit_sample(rng))
        labels.append(0)
    df = pd.DataFrame(rows, columns=FEATURE_NAMES)
    df["label"] = labels
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


def train() -> None:
    total_start = time.time()
    steps = [
        "Dataset generation",
        "Build ensemble model",
        "Cross-validation (5-fold)",
        "Train final model",
        "Evaluation",
        "Save model & metrics",
    ]
    print("=" * 60)
    print("  🛡️  Phishing Detector — Model Training")
    print("=" * 60)
    print(f"  Steps: {len(steps)}")
    for i, s in enumerate(steps, 1):
        print(f"    {i}. {s}")
    print("=" * 60)
    print()

    # ── Step 1: Generate dataset ──────────────────────────────────
    step_start = time.time()
    print(f"[Step 1/{len(steps)}] Generating dataset...")
    df = generate_dataset(1000, 1000)
    X = df[FEATURE_NAMES].values
    y = df["label"].values
    elapsed = time.time() - step_start
    print(f"  ✅ Dataset ready — {len(df)} samples ({elapsed:.1f}s)\n")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # ── Step 2: Build ensemble ────────────────────────────────────
    step_start = time.time()
    print(f"[Step 2/{len(steps)}] Building ensemble model...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    xgb_clf = xgb.XGBClassifier(
        n_estimators=100, use_label_encoder=False,
        eval_metric="logloss", random_state=42, verbosity=0,
    )
    lgb_clf = lgb.LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)

    ensemble = VotingClassifier(
        estimators=[("rf", rf), ("xgb", xgb_clf), ("lgb", lgb_clf)],
        voting="soft",
    )
    elapsed = time.time() - step_start
    print(f"  ✅ Ensemble ready — RF + XGBoost + LightGBM ({elapsed:.1f}s)\n")

    # ── Step 3: Cross-validation ──────────────────────────────────
    step_start = time.time()
    n_folds = 5
    print(f"[Step 3/{len(steps)}] Cross-validating ({n_folds}-fold)...")
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    fold_scores = []
    for fold_idx, (train_idx, val_idx) in enumerate(
        tqdm(skf.split(X_train, y_train), total=n_folds, desc="  CV folds", unit="fold"),
        1,
    ):
        fold_model = VotingClassifier(
            estimators=[
                ("rf", RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)),
                ("xgb", xgb.XGBClassifier(n_estimators=100, use_label_encoder=False,
                                           eval_metric="logloss", random_state=42, verbosity=0)),
                ("lgb", lgb.LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)),
            ],
            voting="soft",
        )
        fold_model.fit(X_train[train_idx], y_train[train_idx])
        proba = fold_model.predict_proba(X_train[val_idx])[:, 1]
        score = roc_auc_score(y_train[val_idx], proba)
        fold_scores.append(score)
    cv_scores = np.array(fold_scores)
    elapsed = time.time() - step_start
    print(f"  ✅ CV AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f} ({elapsed:.1f}s)\n")

    # ── Step 4: Train final model ─────────────────────────────────
    step_start = time.time()
    print(f"[Step 4/{len(steps)}] Training final model on full training set...")
    ensemble.fit(X_train, y_train)
    elapsed = time.time() - step_start
    print(f"  ✅ Training complete ({elapsed:.1f}s)\n")

    # ── Step 5: Evaluate ──────────────────────────────────────────
    step_start = time.time()
    print(f"[Step 5/{len(steps)}] Evaluating on test set...")
    y_pred = ensemble.predict(X_test)
    y_proba = ensemble.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "cv_auc_mean": round(float(cv_scores.mean()), 4),
        "cv_auc_std": round(float(cv_scores.std()), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(
            y_test, y_pred, output_dict=True
        ),
    }
    elapsed = time.time() - step_start
    print(f"  Accuracy: {metrics['accuracy']}")
    print(f"  ROC-AUC:  {metrics['roc_auc']}")
    print(f"  ✅ Evaluation complete ({elapsed:.1f}s)\n")

    # ── Step 6: Save ──────────────────────────────────────────────
    step_start = time.time()
    print(f"[Step 6/{len(steps)}] Saving model and metrics...")
    model_path = MODELS_DIR / "ensemble_model.joblib"
    joblib.dump(ensemble, str(model_path))
    print(f"  Model  → {model_path}")

    results_path = RESULTS_DIR / "metrics.json"
    with open(results_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Metrics → {results_path}")
    elapsed = time.time() - step_start
    print(f"  ✅ Saved ({elapsed:.1f}s)\n")

    # ── Summary ───────────────────────────────────────────────────
    total_elapsed = time.time() - total_start
    minutes, seconds = divmod(int(total_elapsed), 60)
    print("=" * 60)
    print(f"  🎉 Training complete!  Total time: {minutes}m {seconds}s")
    print("=" * 60)


if __name__ == "__main__":
    train()
