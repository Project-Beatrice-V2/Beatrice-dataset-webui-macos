"""Common Voice integration."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def search_common_voice(name: str, language: str = "en") -> list[dict[str, Any]]:
    """Search Common Voice for speaker clips (limited utility for named persons)."""
    return []
