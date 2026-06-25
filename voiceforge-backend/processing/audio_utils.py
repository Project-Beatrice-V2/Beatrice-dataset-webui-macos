"""Core audio manipulation helpers."""

import io
import logging
import subprocess
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)

AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".flac", ".ogg", ".opus", ".aac", ".m4a", ".m4b",
    ".aiff", ".aif", ".webm", ".wma", ".pcm", ".raw",
}


def load_audio(path: Path, target_sr: Optional[int] = None) -> tuple[np.ndarray, int]:
    """Load audio file, optionally resampling."""
    data, sr = sf.read(str(path), always_2d=False)
    if data.ndim > 1:
        data = data.mean(axis=1)
    if target_sr and sr != target_sr:
        data = resample(data, sr, target_sr)
        sr = target_sr
    return data.astype(np.float32), sr


def save_audio(
    path: Path,
    data: np.ndarray,
    sr: int,
    bit_depth: int = 16,
) -> None:
    """Save audio as WAV with specified bit depth."""
    subtype_map = {16: "PCM_16", 24: "PCM_24", 32: "FLOAT"}
    subtype = subtype_map.get(bit_depth, "PCM_16")
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), data, sr, subtype=subtype)


def resample(data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio using scipy."""
    if orig_sr == target_sr:
        return data
    from scipy import signal

    num_samples = int(len(data) * target_sr / orig_sr)
    return signal.resample(data, num_samples).astype(np.float32)


def to_mono(data: np.ndarray) -> np.ndarray:
    if data.ndim == 1:
        return data
    return data.mean(axis=1)


def rms_db(data: np.ndarray) -> float:
    rms = np.sqrt(np.mean(data**2))
    if rms < 1e-10:
        return -100.0
    return float(20 * np.log10(rms))


def estimate_snr(data: np.ndarray, sr: int) -> float:
    """Estimate SNR using signal vs noise floor from quiet segments."""
    frame_len = int(sr * 0.025)
    hop = frame_len // 2
    energies = []
    for i in range(0, len(data) - frame_len, hop):
        frame = data[i : i + frame_len]
        energies.append(np.mean(frame**2))

    if not energies:
        return 0.0

    energies = np.array(energies)
    noise_floor = np.percentile(energies, 10)
    signal_level = np.percentile(energies, 90)

    if noise_floor < 1e-12:
        return 40.0
    snr = 10 * np.log10(signal_level / noise_floor)
    return float(np.clip(snr, 0, 50))


def run_ffmpeg(args: list[str]) -> None:
    """Run ffmpeg command."""
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")


def get_device() -> str:
    """Auto-detect best compute device."""
    from config import get_settings

    setting = get_settings().USE_GPU
    if setting == "cpu":
        return "cpu"
    if setting == "cuda":
        return "cuda"
    if setting == "mps":
        return "mps"
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"
