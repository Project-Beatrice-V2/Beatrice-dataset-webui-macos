"""OpenSLR search + download."""

import logging
from typing import Any
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def search_openslr(query: str) -> list[dict[str, Any]]:
    """Search OpenSLR for named speaker datasets."""
    results = []
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://www.openslr.org/search.php?search={quote(query)}"
            async with session.get(url, timeout=15) as resp:
                if resp.status != 200:
                    return []
                html = await resp.text()

        soup = BeautifulSoup(html, "lxml")
        for row in soup.select("table tr"):
            cols = row.find_all("td")
            if len(cols) >= 2:
                link = cols[0].find("a")
                if link:
                    results.append({
                        "id": link.get("href", ""),
                        "title": link.get_text(strip=True),
                        "description": cols[1].get_text(strip=True) if len(cols) > 1 else "",
                    })
    except Exception as e:
        logger.warning("OpenSLR search failed: %s", e)
    return results
