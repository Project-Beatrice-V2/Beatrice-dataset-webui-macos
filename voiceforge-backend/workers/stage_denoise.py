"""Noise reduction stage."""

import logging
from pathlib import Path
from typing import Any

from processing.audio_utils import load_audio, save_audio
from processing.denoiser import denoise_audio
from processing.normalizer import normalize_audio

logger = logging.getLogger(__name__)


def process_clips(clips: list[dict[str, Any]], options: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply denoising and normalization to all clips."""
    strength = options.get("denoise_strength", "medium")
    bit_depth = options.get("bit_depth", 16)

    for clip in clips:
        path = Path(clip["file_path"])
        if not path.exists():
            continue

        try:
            data, sr = load_audio(path)
            data = denoise_audio(data, sr, strength)
            data = normalize_audio(data)
            save_audio(path, data, sr, bit_depth)
            clip["denoise_applied"] = strength != "off"
            clip["normalized"] = True
        except Exception as e:
            logger.warning("Denoise failed for %s: %s", path, e)
            clip["denoise_applied"] = False

    return clips
