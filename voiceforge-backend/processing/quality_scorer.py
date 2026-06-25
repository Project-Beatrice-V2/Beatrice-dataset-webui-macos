"""Quality scoring logic."""

import numpy as np
import librosa

from processing.audio_utils import estimate_snr


def compute_quality_score(audio_array: np.ndarray, sample_rate: int) -> float:
    """Returns composite 0–100 quality score."""
    score = 0.0

    # 1. SNR Score (0–35 pts)
    snr = estimate_snr(audio_array, sample_rate)
    snr_score = min(35, (snr / 40.0) * 35)
    score += snr_score

    # 2. Duration Score (0–20 pts)
    duration = len(audio_array) / sample_rate
    if 1.5 <= duration <= 10.0:
        dur_score = 20
    elif 10.0 < duration <= 20.0:
        dur_score = 15
    elif 0.5 <= duration < 1.5:
        dur_score = 10
    else:
        dur_score = 5
    score += dur_score

    # 3. Spectral Cleanliness (0–20 pts)
    try:
        spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=audio_array))
        cleanliness_score = max(0, 20 - (spectral_flatness * 200))
    except Exception:
        cleanliness_score = 10
    score += cleanliness_score

    # 4. No Clipping (0–15 pts)
    peak = np.max(np.abs(audio_array))
    clip_score = 0 if peak >= 0.999 else 15
    score += clip_score

    # 5. Silence Ratio (0–10 pts)
    silence_threshold = 0.01
    silence_ratio = np.mean(np.abs(audio_array) < silence_threshold)
    silence_score = max(0, 10 - (silence_ratio * 25))
    score += silence_score

    return float(round(score, 1))



def filter_clips_by_quality(
    clips: list[dict],
    threshold: float,
    min_clips: int = 50,
) -> list[dict]:
    """Filter clips by quality score, auto-lowering threshold if too few pass."""
    current_threshold = threshold
    kept = [c for c in clips if c.get("quality_score", 0) >= current_threshold]

    while len(kept) < min_clips and current_threshold > 30:
        current_threshold = max(30, current_threshold - 10)
        kept = [c for c in clips if c.get("quality_score", 0) >= current_threshold]

    return kept
