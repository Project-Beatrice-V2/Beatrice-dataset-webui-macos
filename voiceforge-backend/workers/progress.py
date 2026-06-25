"""Redis-based progress publishing for Celery workers and WebSocket gateway."""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def publish_progress(
    job_id: str,
    event_type: str,
    stage: str | None = None,
    progress: int | None = None,
    message: str | None = None,
    **kwargs: Any,
) -> None:
    """Publish a progress event to Redis pub/sub (picked up by WebSocket handler)."""
    event = {"event": event_type}
    if stage is not None:
        event["stage"] = stage
    if progress is not None:
        event["progress"] = progress
    if message is not None:
        event["message"] = message
    event.update(kwargs)

    try:
        from workers.celery_app import redis_client

        redis_client.publish(f"job:{job_id}", json.dumps(event))
    except Exception as e:
        logger.warning("Redis publish failed: %s", e)
