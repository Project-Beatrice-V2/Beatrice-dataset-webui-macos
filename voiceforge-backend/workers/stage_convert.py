"""Format conversion stage."""

import logging
from pathlib import Path
from typing import Any

from processing.converter import convert_file

logger = logging.getLogger(__name__)


def convert_all(
    audio_files: list[dict[str, str]],
    output_dir: Path,
    options: dict[str, Any],
) -> list[dict[str, str]]:
    """Convert all downloaded files to normalized WAV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    converted = []
    sample_rate = options.get("target_sample_rate", 22050)
    bit_depth = options.get("bit_depth", 16)
    channels = options.get("channels", "mono")

    for i, af in enumerate(audio_files):
        src_path = Path(af["path"])
        if not src_path.exists():
            continue

        clip_dir = output_dir / f"source_{i:03d}"
        clip_dir.mkdir(parents=True, exist_ok=True)

        try:
            results = convert_file(
                src_path, clip_dir,
                target_format="wav",
                sample_rate=sample_rate,
                bit_depth=bit_depth,
                channels=channels,
                normalize=True,
            )
            for wav_path in results:
                converted.append({
                    "path": str(wav_path),
                    "source": af.get("source", ""),
                    "url": af.get("url", ""),
                    "title": af.get("title", ""),
                })
        except Exception as e:
            logger.error("Conversion failed for %s: %s", src_path, e)

    logger.info("Converted %d WAV files", len(converted))
    return converted
