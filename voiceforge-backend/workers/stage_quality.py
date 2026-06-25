"""Quality scoring + filtering stage."""

import logging
from typing import Any

from processing.audio_utils import estimate_snr, load_audio, rms_db
from processing.quality_scorer import compute_quality_score, filter_clips_by_quality

logger = logging.getLogger(__name__)


def score_and_filter(clips: list[dict[str, Any]], options: dict[str, Any]) -> list[dict[str, Any]]:
    """Score all clips and filter by quality threshold."""
    threshold = options.get("quality_threshold", 60)
    min_snr = options.get("min_snr_db", 15.0)

    for clip in clips:
        from pathlib import Path
        path = Path(clip["file_path"])
        if not path.exists():
            clip["quality_score"] = 0
            clip["kept"] = False
            continue

        try:
            data, sr = load_audio(path)
            clip["snr_db"] = round(estimate_snr(data, sr), 1)
            clip["rms_db"] = round(rms_db(data), 1)
            clip["quality_score"] = compute_quality_score(data, sr)

            if clip["snr_db"] < min_snr:
                clip["kept"] = False
        except Exception as e:
            logger.warning("Quality scoring failed: %s", e)
            clip["quality_score"] = 0

    # Filter by quality threshold
    filtered = filter_clips_by_quality(clips, threshold)
    kept_ids = {id(c) for c in filtered}

    for clip in clips:
        if id(clip) not in kept_ids:
            clip["kept"] = False

    kept_count = sum(1 for c in clips if c.get("kept", True))
    logger.info("Quality filter: %d/%d clips kept (threshold=%d)", kept_count, len(clips), threshold)

    return [c for c in clips if c.get("kept", True)]
