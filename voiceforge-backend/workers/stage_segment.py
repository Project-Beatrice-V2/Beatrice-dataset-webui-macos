"""VAD + audio segmentation stage."""

import logging
from pathlib import Path
from typing import Any

import numpy as np

from processing.audio_utils import load_audio, save_audio
from processing.vad import get_speech_segments, segment_audio

logger = logging.getLogger(__name__)


def segment_all(
    speaker_segments: list[dict[str, Any]],
    output_dir: Path,
    options: dict[str, Any],
) -> list[dict[str, Any]]:
    """Segment audio into clips using VAD."""
    output_dir.mkdir(parents=True, exist_ok=True)
    clips = []
    min_dur = options.get("min_clip_duration_sec", 1.5)
    max_dur = options.get("max_clip_duration_sec", 25.0)
    sample_rate = options.get("target_sample_rate", 22050)
    bit_depth = options.get("bit_depth", 16)
    clip_idx = 0

    for seg_info in speaker_segments:
        src = Path(seg_info["path"])
        if not src.exists():
            continue

        try:
            data, sr = load_audio(src, target_sr=sample_rate)

            # Extract speaker segment first
            start_sample = int(seg_info["start"] * sr)
            end_sample = int(seg_info["end"] * sr)
            segment_data = data[start_sample:end_sample]

            if options.get("use_vad", True):
                # Save temp segment for VAD
                temp_path = output_dir / f"_temp_{clip_idx}.wav"
                save_audio(temp_path, segment_data, sr, bit_depth)
                vad_segments = get_speech_segments(temp_path, sample_rate=sr)
                temp_path.unlink(missing_ok=True)

                # Offset VAD segments to absolute time
                for vs in vad_segments:
                    vs["start"] += seg_info["start"]
                    vs["end"] += seg_info["start"]

                clip_tuples = segment_audio(data, sr, vad_segments, min_dur, max_dur)
            else:
                duration = len(segment_data) / sr
                if min_dur <= duration <= max_dur:
                    clip_tuples = [(segment_data, seg_info["start"], seg_info["end"])]
                else:
                    clip_tuples = []

            for clip_data, start_ts, end_ts in clip_tuples:
                clip_idx += 1
                filename = f"{clip_idx:04d}.wav"
                clip_path = output_dir / filename
                save_audio(clip_path, clip_data, sr, bit_depth)

                clips.append({
                    "filename": filename,
                    "file_path": str(clip_path),
                    "duration_s": round(len(clip_data) / sr, 2),
                    "sample_rate": sr,
                    "start_ts": round(start_ts, 2),
                    "end_ts": round(end_ts, 2),
                    "source_url": seg_info.get("url", ""),
                    "speaker_id": seg_info.get("speaker_id", "SPK_00"),
                    "kept": True,
                })

        except Exception as e:
            logger.error("Segmentation failed for %s: %s", src, e)

    logger.info("Created %d clips", len(clips))
    return clips
