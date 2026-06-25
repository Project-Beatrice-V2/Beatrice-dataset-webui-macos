"""Tests for quality scoring."""

import numpy as np
import pytest

from processing.quality_scorer import compute_quality_score, filter_clips_by_quality


def test_high_quality_sine():
    sr = 22050
    t = np.linspace(0, 3.0, int(sr * 3.0), endpoint=False)
    data = 0.3 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
    score = compute_quality_score(data, sr)
    assert score >= 60


def test_clipped_audio_penalized():
    sr = 22050
    data = np.ones(sr * 2, dtype=np.float32)  # clipped
    score = compute_quality_score(data, sr)
    assert score < 90  # clipping penalty


def test_filter_auto_lowers_threshold():
    clips = [
        {"quality_score": 55, "kept": True},
        {"quality_score": 58, "kept": True},
        {"quality_score": 45, "kept": True},
    ]
    result = filter_clips_by_quality(clips, threshold=70, min_clips=2)
    assert len(result) >= 2
