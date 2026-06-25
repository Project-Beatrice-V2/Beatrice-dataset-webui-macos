"""Whisper transcription stage."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def transcribe_clips(
    clips: list[dict[str, Any]],
    options: dict[str, Any],
    target_language: str = "auto",
) -> list[dict[str, Any]]:
    """Transcribe all clips using faster-whisper and filter by language."""
    try:
        from models.whisper_loader import get_whisper_model
        from config import get_settings

        model = get_whisper_model(get_settings().WHISPER_MODEL)
    except Exception as e:
        logger.error("Failed to load Whisper model: %s", e)
        return clips

    for clip in clips:
        path = Path(clip["file_path"])
        if not path.exists():
            continue

        try:
            transcript, confidence, detected_lang = _transcribe_file(model, path)
            clip["transcript"] = transcript
            clip["confidence"] = confidence
            clip["detected_language"] = detected_lang

            # Filter by language if selected
            # Whisper returns 'ja' for Japanese, while our frontend uses 'jp' or 'both' for en/ja
            if target_language == "en" and detected_lang != "en":
                clip["kept"] = False
                logger.info("Discarding clip %s: language '%s' does not match target 'en'", path.name, detected_lang)
            elif target_language in ("jp", "ja") and detected_lang != "ja":
                clip["kept"] = False
                logger.info("Discarding clip %s: language '%s' does not match target 'ja'", path.name, detected_lang)
            elif target_language == "both" and detected_lang not in ("en", "ja"):
                clip["kept"] = False
                logger.info("Discarding clip %s: language '%s' does not match target 'en' or 'ja'", path.name, detected_lang)

            if confidence < 0.6:
                clip["kept"] = False
        except Exception as e:
            logger.warning("Transcription failed for %s: %s", path, e)
            clip["transcript"] = None
            clip["confidence"] = 0.0
            clip["detected_language"] = "unknown"

    return clips


def _transcribe_file(model, path: Path) -> tuple[str, float, str]:
    """Transcribe a single audio file, returning (transcript, confidence, detected_language)."""
    detected_lang = "unknown"
    try:
        from faster_whisper import WhisperModel
        if isinstance(model, WhisperModel):
            segments, info = model.transcribe(str(path), beam_size=5)
            detected_lang = getattr(info, "language", "unknown")
            texts = []
            confidences = []
            for seg in segments:
                texts.append(seg.text.strip())
                confidences.append(getattr(seg, "avg_logprob", 0))
            transcript = " ".join(texts)
            confidence = min(1.0, max(0.0, 1.0 + (sum(confidences) / max(len(confidences), 1))))
            return transcript, confidence, detected_lang
    except ImportError:
        pass

    # Fallback to openai-whisper
    result = model.transcribe(str(path))
    transcript = result.get("text", "").strip()
    detected_lang = result.get("language", "unknown")
    return transcript, 0.8, detected_lang
