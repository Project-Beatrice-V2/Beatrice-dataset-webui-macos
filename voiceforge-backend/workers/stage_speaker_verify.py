"""Speaker verification worker stage.

Runs after quality filtering to remove clips that don't match the target
speaker's voiceprint. Uses Resemblyzer embeddings for cosine similarity
comparison against a reference built from the best clips.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def verify_clips(
    clips: list[dict[str, Any]],
    options: dict[str, Any],
) -> list[dict[str, Any]]:
    """Verify all clips belong to the target speaker.

    1. Builds a reference voiceprint from the top-quality clips.
    2. Compares every clip and rejects those below the similarity threshold.
    """
    if not clips:
        return clips

    threshold = options.get("speaker_similarity_threshold", 0.75)

    from processing.speaker_verify import build_reference_embedding, verify_speaker

    # Build reference from top clips
    reference = build_reference_embedding(clips, top_n=10)

    if reference is None:
        logger.warning("Skipping speaker verification — no reference embedding")
        return clips

    # Verify all clips against the reference
    verified = verify_speaker(clips, reference, threshold=threshold)

    logger.info(
        "Speaker verification complete: %d/%d clips retained",
        len(verified), len(clips),
    )
    return verified
