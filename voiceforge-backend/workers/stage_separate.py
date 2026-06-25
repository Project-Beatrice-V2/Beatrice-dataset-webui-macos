"""Demucs vocal separation stage."""

import logging
from pathlib import Path
from typing import Any

from models.demucs_loader import separate_vocals

logger = logging.getLogger(__name__)


def separate_all(
    wav_files: list[dict[str, str]],
    output_dir: Path,
    options: dict[str, Any],
) -> list[dict[str, str]]:
    """Separate vocals from all audio files."""
    if not options.get("use_demucs", True):
        return wav_files

    output_dir.mkdir(parents=True, exist_ok=True)
    separated = []

    for af in wav_files:
        src = Path(af["path"])
        try:
            vocals_path = separate_vocals(src, output_dir / src.stem)
            if vocals_path and vocals_path.exists():
                separated.append({**af, "path": str(vocals_path), "demucs_applied": True})
            else:
                separated.append({**af, "demucs_applied": False})
        except Exception as e:
            logger.warning("Demucs failed for %s, using original: %s", src, e)
            separated.append({**af, "demucs_applied": False})

    return separated
