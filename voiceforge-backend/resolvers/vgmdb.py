"""VGMdb scraper for game characters."""

import logging
from typing import Any, Optional
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def search_game_character(name: str) -> Optional[dict[str, Any]]:
    """Search VGMdb for game character voice actor."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://vgmdb.net/search?q={quote(name)}"
            headers = {"User-Agent": "VoiceForge/1.0"}
            async with session.get(url, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

        soup = BeautifulSoup(html, "lxml")
        artist_links = soup.select("a[href*='/artist/']")
        if not artist_links:
            return None

        return {
            "name": name,
            "voice_actor_jp": artist_links[0].get_text(strip=True),
        }
    except Exception as e:
        logger.warning("VGMdb search failed: %s", e)
        return None
