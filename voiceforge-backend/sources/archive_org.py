"""Archive.org search + download."""

import logging
from typing import Any

import yt_dlp

logger = logging.getLogger(__name__)


async def search_archive_org(query: str) -> list[dict[str, Any]]:
    """Search Archive.org for audio collections."""
    results = []
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_result = ydl.extract_info(
                f"https://archive.org/search.php?query={query}+mediatype:audio", download=False
            )
        # Archive.org search via yt-dlp is limited; return empty for now
    except Exception as e:
        logger.warning("Archive.org search failed: %s", e)
    return results


def download_archive_audio(url: str, output_dir: str) -> str | None:
    """Download audio from Archive.org."""
    from sources.youtube import YDL_OPTS_AUDIO
    import os
    from pathlib import Path

    opts = {**YDL_OPTS_AUDIO, "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s")}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            for f in Path(output_dir).glob("*"):
                if f.suffix in (".wav", ".mp3", ".flac", ".ogg"):
                    return str(f)
    except Exception as e:
        logger.error("Archive.org download failed: %s", e)
    return None
