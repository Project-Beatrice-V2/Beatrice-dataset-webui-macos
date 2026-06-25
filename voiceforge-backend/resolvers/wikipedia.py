"""Wikipedia fallback resolver."""

import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


async def search_person(name: str) -> Optional[dict[str, Any]]:
    """Search Wikipedia for person info."""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + name.replace(" ", "_")
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

        return {
            "name": data.get("title", name),
            "aliases": [name],
            "description": data.get("description", ""),
            "wikipedia_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }
    except Exception as e:
        logger.warning("Wikipedia search failed: %s", e)
        return None
