"""MyAnimeList Jikan API client."""

import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)
JIKAN_BASE = "https://api.jikan.moe/v4"


async def search_character(name: str) -> Optional[dict[str, Any]]:
    """Search for character on MAL and return voice actor info."""
    async with aiohttp.ClientSession() as session:
        url = f"{JIKAN_BASE}/characters"
        params = {"q": name, "limit": 5}
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

        characters = data.get("data", [])
        if not characters:
            return None

        char = characters[0]
        char_id = char["mal_id"]

        # Get voice actors
        async with session.get(f"{JIKAN_BASE}/characters/{char_id}/full") as resp:
            if resp.status != 200:
                return _basic_char_info(char)
            full_data = await resp.json()

        char_full = full_data.get("data", {})
        voices = char_full.get("voices", [])

        result = {
            "name": char_full.get("name", name),
            "aliases": [a.get("name", "") for a in char_full.get("nicknames", [])],
            "series": "",
            "mal_id": char_id,
        }

        # Get anime series
        anime_list = char_full.get("anime", [])
        if anime_list:
            result["series"] = anime_list[0].get("anime", {}).get("title", "")

        for v in voices:
            lang = v.get("language", "").lower()
            person = v.get("person", {}).get("name", "")
            if "japanese" in lang:
                result["voice_actor_jp"] = person
            elif "english" in lang:
                result["voice_actor_en"] = person

        return result


def _basic_char_info(char: dict) -> dict:
    return {
        "name": char.get("name", ""),
        "aliases": [],
        "series": "",
        "mal_id": char.get("mal_id"),
    }
