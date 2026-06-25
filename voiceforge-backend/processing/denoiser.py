"""Noise reduction wrapper."""

import logging

import numpy as np

logger = logging.getLogger(__name__)

STRENGTH_MAP = {
    "off": None,
    "light": {"prop_decrease": 0.5, "stationary": False},
    "medium": {"prop_decrease": 0.75, "stationary": True},
    "aggressive": {"prop_decrease": 0.95, "stationary": True},
}


def denoise_audio(
    data: np.ndarray,
    sr: int,
    strength: str = "medium",
) -> np.ndarray:
    """Apply noise reduction with configurable strength."""
    params = STRENGTH_MAP.get(strength)
    if params is None:
        return data

    try:
        import noisereduce as nr

        reduced = nr.reduce_noise(y=data, sr=sr, **params)
        return reduced.astype(np.float32)
    except ImportError:
        logger.warning("noisereduce not installed, skipping denoising")
        return data
    except Exception as e:
        logger.warning("Denoising failed: %s", e)
        return data
