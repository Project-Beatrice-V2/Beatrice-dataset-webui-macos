"""Main Celery task chain orchestrator."""

import asyncio
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from workers.celery_app import celery_app
from config import get_settings
from database import Clip, Job, JobStage, get_db_session

logger = logging.getLogger(__name__)
settings = get_settings()


def _update_job(job_id: str, **kwargs):
    db = get_db_session()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            for k, v in kwargs.items():
                setattr(job, k, v)
            job.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def _add_stage(job_id: str, stage: str, progress: int, message: str = ""):
    db = get_db_session()
    try:
        db.add(JobStage(job_id=job_id, stage=stage, progress=progress, message=message))
        db.commit()
    finally:
        db.close()


def _publish(job_id: str, event_type: str, **kwargs):
    from workers.progress import publish_progress
    publish_progress(job_id, event_type, **kwargs)


def _check_cancelled(job_id: str):
    from workers.celery_app import redis_client
    if redis_client.get(f"job:{job_id}:cancelled") == "1":
        raise Exception("Job cancelled by user")


@celery_app.task(bind=True, name="workers.pipeline.run_pipeline")
def run_pipeline(self, job_id: str):
    """Main pipeline orchestrator — runs all stages sequentially."""
    db = get_db_session()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        db.close()
        return

    options = job.get_options()
    work_dir = settings.TEMP_DIR / job_id
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        _check_cancelled(job_id)
        # STAGE 1: Query Enrichment
        _update_job(job_id, status="searching")
        _add_stage(job_id, "Query Enrichment", 5, "Resolving character metadata")
        _publish(job_id, "stage_start", stage="Query Enrichment", progress=5)

        from workers.stage_enrichment import enrich_query
        character_info = asyncio.run(enrich_query(job.query, job.query_type, job.language))
        job.set_metadata({"character_info": character_info})
        db.commit()

        _publish(job_id, "stage_complete", stage="Query Enrichment", progress=10)

        _check_cancelled(job_id)
        # STAGE 2: Dataset Hub Search
        _add_stage(job_id, "Searching HuggingFace Hub", 12)
        _publish(job_id, "stage_start", stage="Searching HuggingFace Hub", progress=12)

        from workers.stage_search import search_all_sources
        search_results = asyncio.run(search_all_sources(job.query, job.query_type, character_info, options))
        strategy = search_results.get("strategy", "video_scrape")
        _update_job(job_id, strategy=strategy)
        _publish(job_id, "stage_complete", stage="Hub Search", progress=20)

        _check_cancelled(job_id)
        # STAGE 3: Download
        _update_job(job_id, status="downloading")
        _add_stage(job_id, "Downloading sources", 25)
        _publish(job_id, "stage_start", stage="Downloading", progress=25)

        from workers.stage_download import download_sources
        audio_files = asyncio.run(download_sources(search_results, work_dir / "downloads", options))
        source_urls = [f.get("url", f.get("path", "")) for f in audio_files]
        job.set_source_urls(source_urls)
        db.commit()

        _publish(job_id, "stage_complete", stage="Download", progress=35)

        _check_cancelled(job_id)
        # STAGE 4: Convert raw files to WAV
        _add_stage(job_id, "Converting audio", 38)
        from workers.stage_convert import convert_all
        wav_files = convert_all(audio_files, work_dir / "converted", options)

        _check_cancelled(job_id)
        # STAGE 5: Vocal Separation (if video/music sources)
        _update_job(job_id, status="processing")
        if options.get("use_demucs", True) and strategy in ("video_scrape", "hybrid"):
            _add_stage(job_id, "Vocal Separation", 42)
            _publish(job_id, "stage_start", stage="Vocal Separation", progress=42)
            from workers.stage_separate import separate_all
            wav_files = separate_all(wav_files, work_dir / "vocals", options)
            _publish(job_id, "stage_complete", stage="Vocal Separation", progress=50)

        _check_cancelled(job_id)
        # STAGE 6: Speaker Diarization
        _add_stage(job_id, "Speaker Diarization", 52)
        _publish(job_id, "stage_start", stage="Diarization", progress=52)
        from workers.stage_diarize import diarize_all
        speaker_segments = diarize_all(wav_files, character_info, options)
        _publish(job_id, "stage_complete", stage="Diarization", progress=58)

        _check_cancelled(job_id)
        # STAGE 7: Segmentation
        _add_stage(job_id, "Audio Segmentation", 60)
        _publish(job_id, "stage_start", stage="Segmentation", progress=60)
        from workers.stage_segment import segment_all
        clips = segment_all(speaker_segments, work_dir / "clips", options)
        _publish(job_id, "stage_complete", stage="Segmentation", progress=68)

        _check_cancelled(job_id)
        # STAGE 8: Denoise + Quality
        _add_stage(job_id, "Quality Filtering", 70)
        _publish(job_id, "stage_start", stage="Denoising & Quality", progress=70)
        from workers.stage_denoise import process_clips
        from workers.stage_quality import score_and_filter
        clips = process_clips(clips, options)
        clips = score_and_filter(clips, options)
        _publish(job_id, "stage_complete", stage="Quality Filter", progress=76)

        _check_cancelled(job_id)
        # STAGE 8.5: Speaker Verification
        _add_stage(job_id, "Speaker Verification", 78)
        _publish(job_id, "stage_start", stage="Speaker Verify", progress=78)
        from workers.stage_speaker_verify import verify_clips
        clips = verify_clips(clips, options)
        _publish(job_id, "stage_complete", stage="Speaker Verify", progress=82)

        _check_cancelled(job_id)
        # STAGE 9: Transcription
        if options.get("transcribe", True):
            _add_stage(job_id, "Transcription", 82)
            _publish(job_id, "stage_start", stage="Transcription", progress=82)
            from workers.stage_transcribe import transcribe_clips
            clips = transcribe_clips(clips, options, target_language=job.language)
            _publish(job_id, "stage_complete", stage="Transcription", progress=88)

        _check_cancelled(job_id)
        # Save clips to DB
        total_seconds = 0.0
        for i, clip in enumerate(clips):
            db_clip = Clip(
                job_id=job_id,
                filename=clip.get("filename", f"{i+1:04d}.wav"),
                duration_s=clip.get("duration_s", 0),
                sample_rate=clip.get("sample_rate", options.get("target_sample_rate", 22050)),
                snr_db=clip.get("snr_db", 0),
                rms_db=clip.get("rms_db", 0),
                transcript=clip.get("transcript"),
                confidence=clip.get("confidence"),
                speaker_id=clip.get("speaker_id"),
                source_url=clip.get("source_url"),
                start_ts=clip.get("start_ts"),
                end_ts=clip.get("end_ts"),
                quality_score=clip.get("quality_score", 0),
                kept=clip.get("kept", True),
                file_path=clip.get("file_path"),
            )
            db.add(db_clip)
            total_seconds += clip.get("duration_s", 0)

            _publish(job_id, "clip_ready", clip={
                "filename": clip.get("filename"),
                "duration": clip.get("duration_s"),
                "snr": clip.get("snr_db"),
                "quality_score": clip.get("quality_score"),
            })

        _check_cancelled(job_id)
        # STAGE 10: Package
        _update_job(job_id, status="packaging")
        _add_stage(job_id, "Packaging dataset", 90)
        _publish(job_id, "stage_start", stage="Packaging", progress=90)

        from workers.stage_package import package_job
        zip_path = package_job(job_id, clips, character_info, options, search_results.get("sources", []))

        _update_job(
            job_id,
            status="done",
            total_clips=len(clips),
            total_seconds=total_seconds,
            output_path=str(zip_path),
        )
        db.commit()

        _publish(
            job_id, "done",
            clips=len(clips),
            duration_min=round(total_seconds / 60, 1),
            download_url=f"/api/jobs/{job_id}/download",
            progress=100,
        )

    except Exception as e:
        logger.exception("Pipeline failed for job %s", job_id)
        _update_job(job_id, status="failed", error_msg=str(e))
        _publish(job_id, "error", message=str(e), recoverable=True)
    finally:
        db.close()
        # Cleanup temp dir (keep output)
        if work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)


@celery_app.task(name="workers.pipeline.cleanup_old_outputs")
def cleanup_old_outputs():
    """Delete output files older than retention period."""
    cutoff = datetime.utcnow() - timedelta(days=settings.RETENTION_DAYS)
    deleted = 0
    for f in settings.OUTPUT_DIR.glob("*.zip"):
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            f.unlink()
            deleted += 1
    logger.info("Cleaned up %d old output files", deleted)
    return deleted
