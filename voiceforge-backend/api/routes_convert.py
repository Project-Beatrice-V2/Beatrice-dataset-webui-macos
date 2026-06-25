"""Standalone file conversion endpoints."""

import shutil
import uuid
import zipfile
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from config import get_settings
from processing.converter import convert_file
from database import Job, get_db

router = APIRouter(prefix="/api", tags=["convert"])
settings = get_settings()


@router.post("/convert")
async def convert_files(
    files: list[UploadFile] = File(...),
    target_format: str = Form("wav"),
    sample_rate: int = Form(22050),
    bit_depth: int = Form(16),
    channels: str = Form("mono"),
    normalize: bool = Form(True),
    trim_silence: bool = Form(False),
    db: Session = Depends(get_db),
):
    job_id = str(uuid.uuid4())
    work_dir = settings.TEMP_DIR / f"convert_{job_id}"
    output_dir = work_dir / "output"
    work_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    errors: list[str] = []

    for upload in files:
        input_path = work_dir / upload.filename
        with open(input_path, "wb") as f:
            content = await upload.read()
            f.write(content)

        try:
            results = convert_file(
                input_path,
                output_dir,
                target_format=target_format,
                sample_rate=sample_rate,
                bit_depth=bit_depth,
                channels=channels,
                normalize=normalize,
                trim_silence=trim_silence,
            )
            converted += len(results)
        except Exception as e:
            errors.append(f"{upload.filename}: {e}")

    # Package as ZIP
    zip_path = settings.OUTPUT_DIR / f"convert_{job_id}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for wav in output_dir.rglob("*"):
            if wav.is_file():
                zf.write(wav, wav.relative_to(output_dir))

    # Save to database
    from datetime import datetime
    db_job = Job(
        id=job_id,
        query=f"Audio Conversion ({len(files)} files)",
        query_type="conversion",
        status="done" if converted > 0 else "failed",
        total_clips=converted,
        output_path=str(zip_path) if converted > 0 else None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_job.set_options({
        "output_format": target_format,
        "sample_rate": sample_rate,
        "bit_depth": bit_depth,
        "channels": channels,
        "normalize": normalize,
        "trim_silence": trim_silence
    })
    db.add(db_job)
    db.commit()

    return {
        "job_id": job_id,
        "status": db_job.status,
        "files_converted": converted,
        "errors": errors,
        "download_url": f"/api/convert/{job_id}/download",
    }


@router.get("/convert/{job_id}/download")
def download_converted(job_id: str):
    zip_path = settings.OUTPUT_DIR / f"convert_{job_id}.zip"
    if not zip_path.exists():
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Conversion output not found")
    return FileResponse(zip_path, media_type="application/zip", filename=f"converted_{job_id}.zip")
