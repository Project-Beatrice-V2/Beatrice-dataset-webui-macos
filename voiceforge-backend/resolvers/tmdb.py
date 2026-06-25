"""TMDB for live-action actors."""

import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


async def search_actor(name: str, api_key: str = "") -> Optional[dict[str, Any]]:
    """Search TMDB for actor info."""
    if not api_key:
        return None
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.themoviedb.org/3/search/person"
            params = {"api_key": api_key, "query": name}
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        results = data.get("results", [])
        if not results:
            return None

        person = results[0]
        return {
            "name": person.get("name", name),
            "known_for": [w.get("title", "") for w in person.get("known_for", [])],
            "tmdb_id": person.get("id"),
        }
    except Exception as e:
        logger.warning("TMDB search failed: %s", e)
        return None
