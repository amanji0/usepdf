"""File storage service for uploads and results."""

import logging
import time
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
RESULT_DIR = Path(settings.RESULT_DIR)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)


async def save_upload(file: UploadFile) -> tuple[str, Path]:
    """Save an uploaded file with a UUID-based name, preserving its extension.

    Returns the generated file_id and the Path where the file was written.
    """
    ext = Path(file.filename).suffix if file.filename else ".pdf"
    file_id = uuid.uuid4().hex
    dest = UPLOAD_DIR / f"{file_id}{ext}"

    contents = await file.read()
    dest.write_bytes(contents)
    await file.seek(0)

    logger.info("Saved upload %s -> %s (%d bytes)", file_id, dest.name, len(contents))
    return file_id, dest


async def save_uploads(files: list[UploadFile]) -> list[tuple[str, Path]]:
    """Save multiple uploaded files and return their (file_id, path) pairs."""
    results: list[tuple[str, Path]] = []
    for f in files:
        results.append(await save_upload(f))
    return results


def get_upload_path(file_id: str) -> Path:
    """Return the expected upload path for a given file_id.

    Searches UPLOAD_DIR for any file whose stem matches the file_id.
    """
    for p in UPLOAD_DIR.iterdir():
        if p.stem == file_id:
            return p
    return UPLOAD_DIR / f"{file_id}.pdf"


def get_result_path(job_id: str, extension: str = ".pdf") -> Path:
    """Return the result path for a given job, creating parent dirs if needed."""
    if not extension.startswith("."):
        extension = f".{extension}"
    return RESULT_DIR / f"{job_id}{extension}"


def get_result_url(job_id: str) -> str:
    """Return the download URL for a completed job."""
    return f"/api/download/{job_id}"


def cleanup_expired() -> int:
    """Delete files older than FILE_TTL_SECONDS from upload and result dirs.

    Returns the number of files removed.
    """
    ttl = settings.FILE_TTL_SECONDS
    now = time.time()
    removed = 0

    for directory in (UPLOAD_DIR, RESULT_DIR):
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if path.is_file():
                age = now - path.stat().st_mtime
                if age > ttl:
                    path.unlink(missing_ok=True)
                    removed += 1
                    logger.debug("Removed expired file: %s (age=%.0fs)", path.name, age)

    if removed:
        logger.info("Cleanup removed %d expired file(s)", removed)
    return removed
