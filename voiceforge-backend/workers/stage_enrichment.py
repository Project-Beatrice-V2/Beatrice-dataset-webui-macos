"""Query enrichment + character resolution stage."""

import logging
from typing import Any

from resolvers.character_resolver import resolve_character

logger = logging.getLogger(__name__)


async def enrich_query(query: str, query_type: str, language: str) -> dict[str, Any]:
    """Normalize query and resolve character metadata."""
    normalized = query.strip().lower()
    character_info = await resolve_character(query, query_type, language)
    character_info["normalized_query"] = normalized
    character_info["language"] = language if language != "auto" else character_info.get("language", "auto")
    logger.info("Enriched query '%s': %s", query, character_info.get("name"))
    return character_info
