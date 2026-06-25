"""ZIP packaging + metadata generation stage."""

import logging
import shutil
from pathlib import Path
from typing import Any

from config import get_settings
from processing.packager import create_zip, package_dataset_files
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


def package_job(
    job_id: str,
    clips: list[dict[str, Any]],
    character_info: dict[str, Any],
    options: dict[str, Any],
    sources: list[dict[str, Any]],
) -> Path:
    """Package clips into a downloadable ZIP."""
    dataset_dir = settings.OUTPUT_DIR / f"dataset_{job_id}"
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    package_dataset_files(clips, dataset_dir, character_info, options, sources)

    zip_path = settings.OUTPUT_DIR / f"voiceforge_{job_id}.zip"
    create_zip(dataset_dir, zip_path)

    # Cleanup dataset dir after zipping
    shutil.rmtree(dataset_dir, ignore_errors=True)

    logger.info("Packaged dataset: %s (%d clips)", zip_path, len(clips))
    return zip_path


@celery_app.task(name="workers.stage_package.package_dataset")
def package_dataset(job_id: str, options: dict[str, Any] | None = None):
    """Re-package an existing job with updated options."""
    from database import Clip, Job, get_db_session

    db = get_db_session()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        clips_db = db.query(Clip).filter(Clip.job_id == job_id, Clip.kept == True).all()  # noqa: E712
        clips = []
        for c in clips_db:
            clips.append({
                "filename": c.filename,
                "file_path": c.file_path,
                "duration_s": c.duration_s,
                "sample_rate": c.sample_rate,
                "snr_db": c.snr_db,
                "rms_db": c.rms_db,
                "transcript": c.transcript,
                "confidence": c.confidence,
                "speaker_id": c.speaker_id,
                "source_url": c.source_url,
                "start_ts": c.start_ts,
                "end_ts": c.end_ts,
                "quality_score": c.quality_score,
                "kept": c.kept,
            })

        opts = options or job.get_options()
        metadata = job.get_metadata()
        character_info = metadata.get("character_info", {"name": job.query})

        zip_path = package_job(job_id, clips, character_info, opts, job.get_source_urls())
        job.output_path = str(zip_path)
        job.status = "done"
        db.commit()
    finally:
        db.close()
