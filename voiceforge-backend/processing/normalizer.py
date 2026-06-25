"""Audio normalization utilities."""

import numpy as np


def normalize_audio(data: np.ndarray, target_rms_db: float = -20.0, peak_limit: float = 0.99) -> np.ndarray:
    """RMS normalize to target dBFS with peak limiting."""
    rms = np.sqrt(np.mean(data**2))
    if rms < 1e-10:
        return data

    target_rms = 10 ** (target_rms_db / 20)
    data = data * (target_rms / rms)

    peak = np.max(np.abs(data))
    if peak > peak_limit:
        data = data * (peak_limit / peak)

    return data.astype(np.float32)


def loudnorm_ffmpeg(input_path: str, output_path: str, sample_rate: int = 22050) -> None:
    """EBU R128 loudness normalization via ffmpeg."""
    from processing.audio_utils import run_ffmpeg

    run_ffmpeg([
        "-i", input_path,
        "-af", "loudnorm=I=-20:TP=-1:LRA=11",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", "1",
        output_path,
    ])
