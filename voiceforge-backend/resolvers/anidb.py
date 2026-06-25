"""AniDB API client."""

import asyncio
import logging
import xml.etree.ElementTree as ET
from typing import Any, Optional

import aiohttp

from config import get_settings

logger = logging.getLogger(__name__)
ANIDB_API = "http://api.anidb.net:9001/httpapi"


async def search_character_anidb(name: str) -> Optional[dict[str, Any]]:
    """Search AniDB for character voice actor info."""
    settings = get_settings()
    await asyncio.sleep(settings.ANIDB_DELAY_S)

    # AniDB HTTP API requires client name/version registration
    # Fallback: use character name search via anime search
    try:
        async with aiohttp.ClientSession() as session:
            # Search via anime characters endpoint (limited without auth)
            url = f"https://api.jikan.moe/v4/characters"
            params = {"q": name, "limit": 1}
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

            chars = data.get("data", [])
            if not chars:
                return None

            char_id = chars[0]["mal_id"]
            async with session.get(f"https://api.jikan.moe/v4/characters/{char_id}/voices") as resp:
                if resp.status != 200:
                    return None
                voice_data = await resp.json()

            result = {"name": name}
            for v in voice_data.get("data", []):
                lang = v.get("language", "").lower()
                person = v.get("person", {}).get("name", "")
                if "japanese" in lang:
                    result["voice_actor_jp"] = person
                anime = v.get("anime", {})
                if anime and not result.get("series"):
                    result["series"] = anime.get("title", "")

            return result if result.get("voice_actor_jp") else None
    except Exception as e:
        logger.warning("AniDB search failed: %s", e)
        return None
