"""Behind The Voice Actors scraper."""

import logging
import re
from typing import Any, Optional
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
BTVA_SEARCH = "https://www.behindthevoiceactors.com/search/"


async def search_character_va(name: str) -> Optional[dict[str, Any]]:
    """Scrape BTVA for character voice actor info."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BTVA_SEARCH}?search_type=2&dq={quote(name)}"
            headers = {"User-Agent": "VoiceForge/1.0"}
            async with session.get(url, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    return None
                html = await resp.text()

        soup = BeautifulSoup(html, "lxml")
        results = soup.select(".search-result a")
        if not results:
            return None

        char_url = results[0].get("href", "")
        if not char_url.startswith("http"):
            char_url = f"https://www.behindthevoiceactors.com{char_url}"

        async with aiohttp.ClientSession() as session:
            async with session.get(char_url, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    return None
                char_html = await resp.text()

        char_soup = BeautifulSoup(char_html, "lxml")
        result = {"name": name}

        # Extract series from title
        title = char_soup.select_one("h1")
        if title:
            title_text = title.get_text(strip=True)
            match = re.search(r"/(.+)$", title_text)
            if match:
                result["series"] = match.group(1).strip()

        # Find voice actors
        va_sections = char_soup.select(".char-credits")
        for section in va_sections:
            lang_elem = section.select_one(".lang-name")
            va_elem = section.select_one(".va-name a")
            if lang_elem and va_elem:
                lang = lang_elem.get_text(strip=True).lower()
                va_name = va_elem.get_text(strip=True)
                if "english" in lang:
                    result["voice_actor_en"] = va_name
                elif "japanese" in lang:
                    result["voice_actor_jp"] = va_name

        return result if result.get("voice_actor_en") or result.get("voice_actor_jp") else None
    except Exception as e:
        logger.warning("BTVA scrape failed: %s", e)
        return None
