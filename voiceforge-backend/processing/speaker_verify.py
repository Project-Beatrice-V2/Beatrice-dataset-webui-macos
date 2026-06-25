"""Speaker verification using Resemblyzer voice embeddings.

Builds a reference voiceprint from the highest-quality clips (which are most
likely the target speaker after diarization + quality filtering), then compares
every clip against it and discards mismatches.
"""

import logging
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def build_reference_embedding(
    clips: list[dict[str, Any]],
    top_n: int = 10,
) -> np.ndarray | None:
    """Build a reference speaker embedding from the top-N highest quality clips.

    These clips have already survived diarization + quality filtering, so they
    are the most likely to genuinely belong to the target speaker.
    """
    from resemblyzer import VoiceEncoder, preprocess_wav
    from models import get_resemblyzer_encoder

    encoder = get_resemblyzer_encoder()

    # Sort by quality score descending, pick best N
    ranked = sorted(clips, key=lambda c: c.get("quality_score", 0), reverse=True)
    candidates = ranked[:top_n]

    embeddings = []
    for clip in candidates:
        path = Path(clip.get("file_path", ""))
        if not path.exists():
            continue
        try:
            wav = preprocess_wav(path)
            if len(wav) < 1600:  # too short to embed (~0.1s at 16kHz)
                continue
            emb = encoder.embed_utterance(wav)
            embeddings.append(emb)
        except Exception as e:
            logger.debug("Failed to embed reference clip %s: %s", path.name, e)

    if not embeddings:
        logger.warning("Could not build reference embedding — no valid clips")
        return None

    # Outlier detection: filter out clips that don't match the main voice cluster (e.g., side characters)
    if len(embeddings) >= 3:
        filtered_embeddings = []
        for i, emb in enumerate(embeddings):
            sims = [float(np.dot(emb, other)) for j, other in enumerate(embeddings) if i != j]
            mean_sim = np.mean(sims)
            if mean_sim >= 0.70:
                filtered_embeddings.append(emb)
            else:
                logger.info(
                    "Discarded reference candidate clip index %d due to low consistency (mean similarity %.3f)",
                    i, mean_sim,
                )
        if filtered_embeddings:
            embeddings = filtered_embeddings

    # Average all embeddings to create a robust centroid voiceprint
    reference = np.mean(embeddings, axis=0)
    # L2-normalize the centroid so cosine similarity = dot product
    reference = reference / (np.linalg.norm(reference) + 1e-8)
    logger.info(
        "Built reference embedding from %d/%d clips",
        len(embeddings), len(candidates),
    )
    return reference


def verify_speaker(
    clips: list[dict[str, Any]],
    reference_embedding: np.ndarray,
    threshold: float = 0.75,
) -> list[dict[str, Any]]:
    """Compare each clip against the reference embedding.

    Clips with cosine similarity below `threshold` are marked kept=False.
    Returns only the clips that passed verification.
    """
    from resemblyzer import preprocess_wav
    from models import get_resemblyzer_encoder

    encoder = get_resemblyzer_encoder()

    passed = 0
    failed = 0

    for clip in clips:
        path = Path(clip.get("file_path", ""))
        if not path.exists():
            clip["kept"] = False
            clip["speaker_similarity"] = 0.0
            failed += 1
            continue

        try:
            wav = preprocess_wav(path)
            if len(wav) < 1600:
                # Too short to get a meaningful embedding — keep it if quality is good
                clip["speaker_similarity"] = float(threshold)
                passed += 1
                continue

            emb = encoder.embed_utterance(wav)
            # Cosine similarity (both are already L2-normalized by Resemblyzer)
            similarity = float(np.dot(reference_embedding, emb))
            clip["speaker_similarity"] = round(similarity, 3)

            if similarity < threshold:
                clip["kept"] = False
                failed += 1
            else:
                passed += 1

        except Exception as e:
            logger.debug("Speaker verify failed for %s: %s", path.name, e)
            # On error, keep the clip but mark similarity as unknown
            clip["speaker_similarity"] = float(threshold)
            passed += 1

    logger.info(
        "Speaker verify: %d/%d clips passed (threshold=%.2f)",
        passed, passed + failed, threshold,
    )

    return [c for c in clips if c.get("kept", True)]
