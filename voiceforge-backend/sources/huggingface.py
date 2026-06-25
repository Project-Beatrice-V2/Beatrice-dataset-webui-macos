"""HuggingFace Hub search + download."""

import logging
from typing import Any

import aiohttp

from config import get_settings

logger = logging.getLogger(__name__)
HF_API = "https://huggingface.co/api/datasets"


async def search_huggingface(query: str, character_info: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Search HuggingFace Hub for voice datasets."""
    settings = get_settings()
    search_terms = _build_search_terms(query, character_info)
    results = []
    seen_ids = set()

    async with aiohttp.ClientSession() as session:
        for term in search_terms:
            params = {"search": term, "sort": "downloads", "direction": -1, "limit": 10}
            headers = {}
            if settings.HF_TOKEN:
                headers["Authorization"] = f"Bearer {settings.HF_TOKEN}"

            try:
                async with session.get(HF_API, params=params, headers=headers, timeout=15) as resp:
                    if resp.status != 200:
                        continue
                    datasets = await resp.json()

                for ds in datasets:
                    ds_id = ds.get("id", "")
                    if ds_id in seen_ids:
                        continue
                    seen_ids.add(ds_id)

                    # Check if dataset likely contains audio
                    tags = ds.get("tags", [])
                    card_data = ds.get("cardData", {}) or {}
                    if _is_audio_dataset(ds, tags, card_data):
                        results.append({
                            "id": ds_id,
                            "downloads": ds.get("downloads", 0),
                            "likes": ds.get("likes", 0),
                            "tags": tags,
                            "size_gb": _estimate_size(ds),
                            "clips": _estimate_clips(ds),
                        })
            except Exception as e:
                logger.warning("HF search failed for '%s': %s", term, e)

    results.sort(key=lambda x: x.get("downloads", 0), reverse=True)
    return results[:10]


def _build_search_terms(query: str, character_info: dict | None) -> list[str]:
    terms = [
        f"{query} voice",
        f"{query} tts dataset",
        f"{query} audio",
        f"{query} speech",
    ]
    if character_info:
        if character_info.get("series"):
            terms.append(f"{character_info['series']} voice dataset")
        if character_info.get("voice_actor_jp"):
            terms.append(f"{character_info['voice_actor_jp']} voice")
        if character_info.get("voice_actor_en"):
            terms.append(f"{character_info['voice_actor_en']} speech")
    return terms


def _is_audio_dataset(ds: dict, tags: list, card_data: dict) -> bool:
    audio_keywords = {"audio", "speech", "voice", "tts", "asr", "wav", "sound"}
    all_text = " ".join(tags + [ds.get("id", ""), str(card_data)]).lower()
    return any(kw in all_text for kw in audio_keywords)


def _estimate_size(ds: dict) -> float:
    siblings = ds.get("siblings", [])
    total = sum(s.get("size", 0) for s in siblings if isinstance(s, dict))
    return round(total / (1024**3), 2) if total else 0.5


def _estimate_clips(ds: dict) -> int:
    downloads = ds.get("downloads", 0)
    if downloads > 1000:
        return min(downloads // 10, 10000)
    return 500


async def download_hf_dataset(dataset_id: str, output_dir: str) -> list[str]:
    """Download a HuggingFace dataset and return list of audio file paths."""
    from huggingface_hub import snapshot_download
    from pathlib import Path

    settings = get_settings()
    token = settings.HF_TOKEN or None

    local_dir = snapshot_download(
        repo_id=dataset_id,
        repo_type="dataset",
        token=token,
        local_dir=output_dir,
    )

    audio_files = []
    output_path = Path(local_dir)
    for ext in (".wav", ".mp3", ".flac", ".ogg", ".opus", ".m4a", ".parquet"):
        audio_files.extend(str(f) for f in output_path.rglob(f"*{ext}"))

    return audio_files
