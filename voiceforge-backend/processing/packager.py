"""Dataset packaging — ZIP + metadata generation."""

import json
import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from processing.audio_utils import estimate_snr, rms_db

logger = logging.getLogger(__name__)


def package_dataset_files(
    clips: list[dict[str, Any]],
    output_dir: Path,
    character_info: dict[str, Any],
    options: dict[str, Any],
    sources: list[dict[str, Any]],
) -> Path:
    """Package clips into a dataset directory with metadata."""
    wavs_dir = output_dir / "wavs"
    wavs_dir.mkdir(parents=True, exist_ok=True)

    output_format = options.get("output_format", "ljspeech")
    sample_rate = options.get("target_sample_rate", 22050)
    bit_depth = options.get("bit_depth", 16)

    kept_clips = [c for c in clips if c.get("kept", True)]
    metadata_clips = []

    for i, clip in enumerate(kept_clips, 1):
        src = Path(clip["file_path"])
        if not src.exists():
            continue

        filename = f"{i:04d}.wav"
        dest = wavs_dir / filename

        import shutil
        shutil.copy2(src, dest)

        metadata_clips.append({
            "filename": filename,
            "duration_s": float(clip.get("duration_s", 0.0) or 0.0),
            "transcript": clip.get("transcript", ""),
            "transcript_confidence": float(clip.get("confidence", 0.0) or 0.0),
            "snr_db": float(clip.get("snr_db", 0.0) or 0.0),
            "rms_db": float(clip.get("rms_db", 0.0) or 0.0),
            "quality_score": float(clip.get("quality_score", 0.0) or 0.0),
            "source_url": clip.get("source_url", ""),
            "source_timestamp_start": float(clip.get("start_ts", 0.0) or 0.0),
            "source_timestamp_end": float(clip.get("end_ts", 0.0) or 0.0),
            "processing": {
                "demucs_applied": bool(clip.get("demucs_applied", False)),
                "denoise_applied": bool(clip.get("denoise_applied", False)),
                "normalized": bool(clip.get("normalized", True)),
            },
        })

    total_duration = sum(c["duration_s"] for c in metadata_clips)
    mean_snr = sum(c["snr_db"] for c in metadata_clips) / max(len(metadata_clips), 1)
    mean_quality = sum(c["quality_score"] for c in metadata_clips) / max(len(metadata_clips), 1)

    dataset_info = {
        "character": character_info.get("name", ""),
        "aliases": character_info.get("aliases", []),
        "series": character_info.get("series", ""),
        "language": character_info.get("language", "auto"),
        "voice_actor": character_info.get("voice_actor_jp", character_info.get("voice_actor", "")),
        "voice_actor_en": character_info.get("voice_actor_en", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_clips": len(metadata_clips),
        "total_duration_seconds": round(total_duration, 1),
        "mean_duration_seconds": round(total_duration / max(len(metadata_clips), 1), 2),
        "mean_snr_db": round(mean_snr, 1),
        "mean_quality_score": round(mean_quality, 1),
        "sample_rate": sample_rate,
        "bit_depth": bit_depth,
        "channels": options.get("channels", "mono"),
    }

    full_metadata = {
        "dataset_info": dataset_info,
        "sources": sources,
        "clips": metadata_clips,
    }

    # Write metadata files
    (output_dir / "metadata.json").write_text(json.dumps(full_metadata, indent=2, ensure_ascii=False))

    # LJSpeech format CSV
    csv_lines = ["filename|transcript|normalized_transcript"]
    for c in metadata_clips:
        transcript = c.get("transcript", "")
        normalized = transcript.lower().strip()
        csv_lines.append(f"{c['filename']}|{transcript}|{normalized}")
    (output_dir / "metadata.csv").write_text("\n".join(csv_lines))

    # RVC filelist
    speaker_name = character_info.get("name", "speaker").replace(" ", "_")
    rvc_lines = [f"wavs/{c['filename']}|{speaker_name}" for c in metadata_clips]
    (output_dir / "filelist.txt").write_text("\n".join(rvc_lines))

    # Speaker info
    speaker_info = {
        "speaker_id": speaker_name,
        "character": character_info.get("name", ""),
        "series": character_info.get("series", ""),
        "language": character_info.get("language", ""),
        "voice_actor": character_info.get("voice_actor_jp", ""),
        "voice_actor_en": character_info.get("voice_actor_en", ""),
    }
    (output_dir / "speaker_info.json").write_text(json.dumps(speaker_info, indent=2))

    # Stats
    quality_buckets = {"90-100": 0, "80-90": 0, "70-80": 0, "60-70": 0, "below-60": 0}
    for c in metadata_clips:
        q = c["quality_score"]
        if q >= 90:
            quality_buckets["90-100"] += 1
        elif q >= 80:
            quality_buckets["80-90"] += 1
        elif q >= 70:
            quality_buckets["70-80"] += 1
        elif q >= 60:
            quality_buckets["60-70"] += 1
        else:
            quality_buckets["below-60"] += 1

    stats = {
        "quality_distribution": quality_buckets,
        "total_clips": len(metadata_clips),
        "total_duration_seconds": round(total_duration, 1),
        "mean_snr_db": round(mean_snr, 1),
        "mean_quality_score": round(mean_quality, 1),
    }
    (output_dir / "stats.json").write_text(json.dumps(stats, indent=2))

    # README
    readme = _generate_readme(dataset_info, sources, stats)
    (output_dir / "README.md").write_text(readme)

    return output_dir


def create_zip(dataset_dir: Path, zip_path: Path) -> Path:
    """Create ZIP archive from dataset directory."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in dataset_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(dataset_dir.parent))
    return zip_path


def _generate_readme(info: dict, sources: list, stats: dict) -> str:
    return f"""# VoiceForge Dataset — {info.get('character', 'Unknown')}

Generated by VoiceForge Dataset Studio on {info.get('created_at', '')}.

## Dataset Info

| Field | Value |
|-------|-------|
| Character | {info.get('character', '')} |
| Series | {info.get('series', '')} |
| Language | {info.get('language', '')} |
| Voice Actor (JP) | {info.get('voice_actor', '')} |
| Voice Actor (EN) | {info.get('voice_actor_en', '')} |
| Total Clips | {info.get('total_clips', 0)} |
| Total Duration | {info.get('total_duration_seconds', 0):.1f}s |
| Mean SNR | {info.get('mean_snr_db', 0):.1f} dB |
| Mean Quality | {info.get('mean_quality_score', 0):.1f}/100 |
| Sample Rate | {info.get('sample_rate', 22050)} Hz |
| Bit Depth | {info.get('bit_depth', 16)}-bit |
| Channels | {info.get('channels', 'mono')} |

## Sources

{chr(10).join(f"- **{s.get('type', '')}**: {s.get('url', s.get('dataset', ''))} ({s.get('clips_extracted', 0)} clips)" for s in sources)}

## Quality Distribution

{chr(10).join(f"- Score {k}: {v} clips" for k, v in stats.get('quality_distribution', {}).items())}

## Usage

### LJSpeech / Coqui TTS
```
metadata.csv  →  filename|transcript|normalized_transcript
wavs/         →  audio files
```

### RVC / Diff-SVC
```
filelist.txt  →  wavs/0001.wav|speaker_name
```

## License

Audio sourced from publicly available content. Verify licensing before commercial use.
"""
