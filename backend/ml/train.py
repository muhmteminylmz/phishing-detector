"""
Training script for the ensemble phishing detection model.
Generates a realistic synthetic dataset, trains an ensemble model,
evaluates it, and saves the result to ml/models/.

Supports checkpoint/resume: if the process is interrupted (e.g. PC
shutdown), re-running this script will skip already-completed steps.
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
CHECKPOINT_DIR = Path(__file__).parent / "checkpoints"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_EXTRACTOR = FeatureExtractor()
FEATURE_NAMES = FEATURE_EXTRACTOR._feature_names()

CHECKPOINT_PATH = CHECKPOINT_DIR / "training_state.json"


def _save_checkpoint(step: int, data: dict | None = None) -> None:
    """Persist current training progress so we can resume later."""
    state = {"completed_step": step}
    if data:
        state["data"] = data
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(state, f)


def _load_checkpoint() -> dict | None:
    """Return the last saved checkpoint, or *None* if none exists."""
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH) as f:
            return json.load(f)
    return None


def _clear_checkpoint() -> None:
    """Remove the checkpoint file after training finishes successfully."""
    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()


def _build_ensemble() -> VotingClassifier:
    """Create a fresh ensemble classifier with the standard configuration."""
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    xgb_clf = xgb.XGBClassifier(
        n_estimators=100, use_label_encoder=False,
        eval_metric="logloss", random_state=42, verbosity=0,
    )
    lgb_clf = lgb.LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)
    return VotingClassifier(
        estimators=[("rf", rf), ("xgb", xgb_clf), ("lgb", lgb_clf)],
        voting="soft",
    )


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
    step_names = [
        "Dataset generation",
        "Build ensemble model",
        "Cross-validation (5-fold)",
        "Train final model",
        "Evaluation",
        "Save model & metrics",
    ]
    total_steps = len(step_names)

    # ── Check for a previous checkpoint ───────────────────────────
    checkpoint = _load_checkpoint()
    resume_after = checkpoint["completed_step"] if checkpoint else 0

    print("=" * 60)
    print("  🛡️  Phishing Detector — Model Training")
    print("=" * 60)
    print(f"  Steps: {total_steps}")
    for i, s in enumerate(step_names, 1):
        marker = "✅" if i <= resume_after else f" {i}."
        print(f"    {marker} {s}")
    if resume_after:
        print(f"\n  ▶ Resuming from step {resume_after + 1} "
              f"(steps 1-{resume_after} already done)")
    print("=" * 60)
    print()

    step_times: list[float] = []

    def _eta() -> str:
        """Estimate remaining time based on elapsed step times."""
        if not step_times:
            return ""
        avg = sum(step_times) / len(step_times)
        done = resume_after + len(step_times)
        remaining = max(total_steps - done, 0)
        secs = int(avg * remaining)
        if secs < 60:
            return f"  ⏱️  Estimated remaining: ~{secs}s"
        minutes, seconds = divmod(secs, 60)
        return f"  ⏱️  Estimated remaining: ~{minutes}m {seconds}s"

    # ── Step 1: Generate dataset ──────────────────────────────────
    if resume_after < 1:
        step_start = time.time()
        print(f"[Step 1/{total_steps}] Generating dataset...")
        df = generate_dataset(1000, 1000)
        X = df[FEATURE_NAMES].values
        y = df["label"].values
        elapsed = time.time() - step_start
        step_times.append(elapsed)
        print(f"  ✅ Dataset ready — {len(df)} samples ({elapsed:.1f}s)")
        print(_eta())
        print()
        # Save dataset to checkpoint so we can reload on resume
        dataset_ckpt = CHECKPOINT_DIR / "dataset.npz"
        np.savez(str(dataset_ckpt), X=X, y=y)
        _save_checkpoint(1)
    else:
        print(f"[Step 1/{total_steps}] Dataset — loaded from checkpoint ✅")
        dataset_ckpt = CHECKPOINT_DIR / "dataset.npz"
        data = np.load(str(dataset_ckpt))
        X, y = data["X"], data["y"]
        print()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # ── Step 2: Build ensemble ────────────────────────────────────
    step_start = time.time()
    if resume_after < 2:
        print(f"[Step 2/{total_steps}] Building ensemble model...")
    else:
        print(f"[Step 2/{total_steps}] Ensemble model — rebuilt ✅")
    ensemble = _build_ensemble()
    elapsed = time.time() - step_start
    step_times.append(elapsed)
    if resume_after < 2:
        print(f"  ✅ Ensemble ready — RF + XGBoost + LightGBM ({elapsed:.1f}s)")
        print(_eta())
        _save_checkpoint(2)
    print()

    # ── Step 3: Cross-validation ──────────────────────────────────
    if resume_after < 3:
        step_start = time.time()
        n_folds = 5
        print(f"[Step 3/{total_steps}] Cross-validating ({n_folds}-fold)...")
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        fold_scores = []
        # Check if some folds were already completed
        cv_ckpt = checkpoint.get("data", {}) if checkpoint else {}
        start_fold = len(cv_ckpt.get("fold_scores", []))
        if start_fold:
            fold_scores = cv_ckpt["fold_scores"]
            print(f"  ▶ Resuming CV from fold {start_fold + 1}/{n_folds}")
        for fold_idx, (train_idx, val_idx) in enumerate(
            tqdm(skf.split(X_train, y_train), total=n_folds, desc="  CV folds",
                 unit="fold", initial=start_fold),
            1,
        ):
            if fold_idx <= start_fold:
                continue
            fold_model = _build_ensemble()
            fold_model.fit(X_train[train_idx], y_train[train_idx])
            proba = fold_model.predict_proba(X_train[val_idx])[:, 1]
            score = roc_auc_score(y_train[val_idx], proba)
            fold_scores.append(score)
            # Checkpoint after each fold
            _save_checkpoint(2, {"fold_scores": fold_scores})
        cv_scores = np.array(fold_scores)
        elapsed = time.time() - step_start
        step_times.append(elapsed)
        print(f"  ✅ CV AUC: {cv_scores.mean():.4f} ± {cv_scores.std():.4f} ({elapsed:.1f}s)")
        print(_eta())
        print()
        _save_checkpoint(3, {"cv_auc_mean": float(cv_scores.mean()),
                             "cv_auc_std": float(cv_scores.std())})
    else:
        cv_data = checkpoint.get("data", {})
        cv_scores = np.array([cv_data.get("cv_auc_mean", 0.0)])
        print(f"[Step 3/{total_steps}] Cross-validation — loaded from checkpoint ✅")
        print(f"  CV AUC: {cv_data.get('cv_auc_mean', 0):.4f} ± {cv_data.get('cv_auc_std', 0):.4f}")
        print()

    # ── Step 4: Train final model ─────────────────────────────────
    if resume_after < 4:
        step_start = time.time()
        print(f"[Step 4/{total_steps}] Training final model on full training set...")
        ensemble.fit(X_train, y_train)
        elapsed = time.time() - step_start
        step_times.append(elapsed)
        print(f"  ✅ Training complete ({elapsed:.1f}s)")
        print(_eta())
        print()
        model_path = MODELS_DIR / "ensemble_model.joblib"
        joblib.dump(ensemble, str(model_path))
        _save_checkpoint(4, {"cv_auc_mean": float(cv_scores.mean()),
                             "cv_auc_std": float(cv_scores.std()) if len(cv_scores) > 1 else 0.0})
    else:
        model_path = MODELS_DIR / "ensemble_model.joblib"
        ensemble = joblib.load(str(model_path))
        print(f"[Step 4/{total_steps}] Final model — loaded from checkpoint ✅")
        print()

    # ── Step 5: Evaluate ──────────────────────────────────────────
    if resume_after < 5:
        step_start = time.time()
        print(f"[Step 5/{total_steps}] Evaluating on test set...")
        y_pred = ensemble.predict(X_test)
        y_proba = ensemble.predict_proba(X_test)[:, 1]

        cv_mean = float(cv_scores.mean())
        cv_std = float(cv_scores.std()) if len(cv_scores) > 1 else 0.0
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
            "cv_auc_mean": round(cv_mean, 4),
            "cv_auc_std": round(cv_std, 4),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(
                y_test, y_pred, output_dict=True
            ),
        }
        elapsed = time.time() - step_start
        step_times.append(elapsed)
        print(f"  Accuracy: {metrics['accuracy']}")
        print(f"  ROC-AUC:  {metrics['roc_auc']}")
        print(f"  ✅ Evaluation complete ({elapsed:.1f}s)")
        print(_eta())
        print()
        _save_checkpoint(5)
    else:
        print(f"[Step 5/{total_steps}] Evaluation — loaded from checkpoint ✅")
        results_path = RESULTS_DIR / "metrics.json"
        with open(results_path) as f:
            metrics = json.load(f)
        print(f"  Accuracy: {metrics['accuracy']}")
        print(f"  ROC-AUC:  {metrics['roc_auc']}")
        print()

    # ── Step 6: Save ──────────────────────────────────────────────
    step_start = time.time()
    print(f"[Step 6/{total_steps}] Saving model and metrics...")
    model_path = MODELS_DIR / "ensemble_model.joblib"
    if resume_after < 4:
        joblib.dump(ensemble, str(model_path))
    print(f"  Model  → {model_path}")

    results_path = RESULTS_DIR / "metrics.json"
    with open(results_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Metrics → {results_path}")
    elapsed = time.time() - step_start
    step_times.append(elapsed)
    print(f"  ✅ Saved ({elapsed:.1f}s)\n")

    # ── Cleanup checkpoint ────────────────────────────────────────
    _clear_checkpoint()
    dataset_ckpt = CHECKPOINT_DIR / "dataset.npz"
    if dataset_ckpt.exists():
        dataset_ckpt.unlink()

    # ── Summary ───────────────────────────────────────────────────
    total_elapsed = time.time() - total_start
    minutes, seconds = divmod(int(total_elapsed), 60)
    print("=" * 60)
    print(f"  🎉 Training complete!  Total time: {minutes}m {seconds}s")
    if resume_after:
        print(f"  (resumed from step {resume_after + 1})")
    print("=" * 60)


if __name__ == "__main__":
    train()
