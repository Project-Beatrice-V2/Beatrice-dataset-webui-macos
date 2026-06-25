"""Demucs model loader."""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def separate_vocals(
    audio_path: Path,
    output_dir: Path,
    model_name: str = "htdemucs_ft",
) -> Path | None:
    """Separate vocals from audio using Demucs."""
    try:
        import sys
        from processing.audio_utils import get_device
        device = get_device()
        
        output_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable, "-m", "demucs",
            "-d", device,
            "-n", model_name,
            "--two-stems", "vocals",
            "-o", str(output_dir),
            str(audio_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            logger.error("Demucs failed: %s", result.stderr)
            return None

        vocals_path = output_dir / model_name / audio_path.stem / "vocals.wav"
        if not vocals_path.exists():
            # Try without --mp3 flag output structure
            for p in output_dir.rglob("vocals.wav"):
                return p
            return None
        return vocals_path
    except Exception as e:
        logger.error("Demucs separation failed: %s", e)
        return None
