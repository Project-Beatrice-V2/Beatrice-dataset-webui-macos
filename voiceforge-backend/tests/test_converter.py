"""Tests for the format conversion engine."""

import io
import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from processing.converter import convert_file
from processing.quality_scorer import compute_quality_score
from processing.audio_utils import estimate_snr, resample
from processing.normalizer import normalize_audio


@pytest.fixture
def sample_wav(tmp_path):
    """Create a sample WAV file."""
    sr = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    data = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
    path = tmp_path / "test.wav"
    sf.write(str(path), data, sr)
    return path, data, sr


def test_load_and_resample(sample_wav):
    path, data, sr = sample_wav
    from processing.audio_utils import load_audio
    loaded, loaded_sr = load_audio(path, target_sr=16000)
    assert loaded_sr == 16000
    assert len(loaded) < len(data)


def test_convert_wav_to_wav(sample_wav):
    path, _, _ = sample_wav
    output_dir = path.parent / "output"
    output_dir.mkdir()
    results = convert_file(path, output_dir, sample_rate=22050, bit_depth=16, channels="mono")
    assert len(results) == 1
    assert results[0].exists()


def test_quality_scorer(sample_wav):
    _, data, sr = sample_wav
    score = compute_quality_score(data, sr)
    assert 0 <= score <= 100
    assert score > 30  # Clean sine wave should score well


def test_snr_estimation(sample_wav):
    _, data, sr = sample_wav
    snr = estimate_snr(data, sr)
    assert snr >= 0


def test_normalize_audio(sample_wav):
    _, data, _ = sample_wav
    normalized = normalize_audio(data)
    rms = np.sqrt(np.mean(normalized**2))
    target_rms = 10 ** (-20 / 20)
    assert abs(rms - target_rms) < 0.1


def test_convert_npy(tmp_path):
    data = np.random.randn(22050).astype(np.float32) * 0.1
    npy_path = tmp_path / "test.npy"
    np.save(str(npy_path), data)
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    results = convert_file(npy_path, output_dir, sample_rate=22050)
    assert len(results) == 1
    assert results[0].suffix == ".wav"
