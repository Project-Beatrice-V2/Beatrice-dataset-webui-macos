"""Celery application configuration."""

import json
import logging

import redis
from celery import Celery

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

celery_app = Celery(
    "voiceforge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "workers.pipeline",
        "workers.stage_enrichment",
        "workers.stage_search",
        "workers.stage_download",
        "workers.stage_convert",
        "workers.stage_separate",
        "workers.stage_diarize",
        "workers.stage_segment",
        "workers.stage_denoise",
        "workers.stage_quality",
        "workers.stage_speaker_verify",
        "workers.stage_transcribe",
        "workers.stage_package",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,
    beat_schedule={
        "cleanup-old-outputs": {
            "task": "workers.pipeline.cleanup_old_outputs",
            "schedule": 86400.0,  # daily
        },
    },
)

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
