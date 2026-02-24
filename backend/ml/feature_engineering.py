"""
Feature engineering utilities shared between training and inference.
"""
from typing import List
import numpy as np
import pandas as pd

from app.models.feature_extractor import FeatureExtractor


def get_feature_names() -> List[str]:
    return FeatureExtractor()._feature_names()


def impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Replace sentinel values (-1) with median for numeric features."""
    for col in df.columns:
        if df[col].dtype in [np.float64, np.int64]:
            df[col] = df[col].replace(-1, df[col].median())
    return df
