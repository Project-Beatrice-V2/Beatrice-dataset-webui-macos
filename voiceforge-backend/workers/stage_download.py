"""Download stage — yt-dlp + HF download."""

import logging
from pathlib import Path
from typing import Any

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def download_sources(
    search_results: dict[str, Any],
    output_dir: Path,
    options: dict[str, Any],
) -> list[dict[str, str]]:
    """Download audio from all found sources."""
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []
    strategy = search_results.get("strategy", "video_scrape")
    max_downloads = settings.MAX_CONCURRENT_DOWNLOADS

    # HuggingFace datasets
    if strategy in ("dataset_hub", "hybrid"):
        from sources.huggingface import download_hf_dataset

        for hf in search_results.get("hf_results", [])[:2]:
            try:
                ds_dir = str(output_dir / f"hf_{hf['id'].replace('/', '_')}")
                files = await download_hf_dataset(hf["id"], ds_dir)
                for f in files:
                    downloaded.append({"path": f, "source": "huggingface", "dataset": hf["id"]})
            except Exception as e:
                logger.error("HF download failed for %s: %s", hf["id"], e)

    # YouTube videos
    if strategy in ("video_scrape", "hybrid"):
        from sources.youtube import download_youtube_audio

        yt_videos = search_results.get("yt_results", [])[:max_downloads * 3]
        for i, video in enumerate(yt_videos):
            try:
                path = download_youtube_audio(video["url"], str(output_dir / "youtube"))
                if path:
                    downloaded.append({"path": path, "source": "youtube", "url": video["url"], "title": video.get("title", "")})
            except Exception as e:
                logger.error("YouTube download failed: %s", e)

    # Bilibili
    if search_results.get("bili_results"):
        from sources.bilibili import download_bilibili_audio

        for video in search_results["bili_results"][:max_downloads]:
            url = video.get("url", "")
            if not url:
                continue
            try:
                path = download_bilibili_audio(url, str(output_dir / "bilibili"))
                if path:
                    downloaded.append({"path": path, "source": "bilibili", "url": url})
            except Exception as e:
                logger.error("Bilibili download failed: %s", e)

    logger.info("Downloaded %d audio files", len(downloaded))
    return downloaded
