"""Tests for training checkpoint / resume functionality."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest


def _tmp_checkpoint_path() -> Path:
    """Create a temporary file path for checkpoint testing."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)  # We want the path, not the file itself
    return Path(path)


def test_save_and_load_checkpoint() -> None:
    """Checkpoint round-trips through JSON correctly."""
    from ml.train import _save_checkpoint, _load_checkpoint

    tmp_path = _tmp_checkpoint_path()
    with patch("ml.train.CHECKPOINT_PATH", tmp_path):
        try:
            # No checkpoint yet
            assert _load_checkpoint() is None

            # Save step 2
            _save_checkpoint(2, {"fold_scores": [0.99, 0.98]})
            ckpt = _load_checkpoint()
            assert ckpt is not None
            assert ckpt["completed_step"] == 2
            assert ckpt["data"]["fold_scores"] == [0.99, 0.98]
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


def test_clear_checkpoint() -> None:
    """_clear_checkpoint removes the file."""
    from ml.train import _save_checkpoint, _clear_checkpoint, _load_checkpoint

    tmp_path = _tmp_checkpoint_path()
    with patch("ml.train.CHECKPOINT_PATH", tmp_path):
        try:
            _save_checkpoint(1)
            assert _load_checkpoint() is not None
            _clear_checkpoint()
            assert _load_checkpoint() is None
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


def test_checkpoint_without_data() -> None:
    """Checkpoint works when no extra data is provided."""
    from ml.train import _save_checkpoint, _load_checkpoint

    tmp_path = _tmp_checkpoint_path()
    with patch("ml.train.CHECKPOINT_PATH", tmp_path):
        try:
            _save_checkpoint(4)
            ckpt = _load_checkpoint()
            assert ckpt["completed_step"] == 4
            assert "data" not in ckpt
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
