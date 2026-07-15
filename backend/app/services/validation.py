"""File validation service for uploads."""

import logging

import magic
from fastapi import HTTPException, UploadFile

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

MAGIC_READ_SIZE = 2048


async def validate_file_type(file: UploadFile, allowed_mimes: set[str]) -> str:
    """Detect the MIME type of *file* using libmagic and verify it is allowed.

    Raises HTTPException 415 if the MIME type is not in *allowed_mimes*.
    Always seeks the file back to the beginning before returning.
    """
    header = await file.read(MAGIC_READ_SIZE)
    try:
        detected = magic.from_buffer(header, mime=True)
    except Exception:
        logger.exception("python-magic failed to detect MIME type")
        detected = file.content_type or "application/octet-stream"
    finally:
        await file.seek(0)

    if detected not in allowed_mimes:
        logger.warning(
            "Rejected upload %s: detected MIME %s not in %s",
            file.filename,
            detected,
            allowed_mimes,
        )
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {detected}. Allowed: {', '.join(sorted(allowed_mimes))}",
        )

    return detected


async def validate_file_size(file: UploadFile, max_mb: int | None = None) -> None:
    """Ensure the file does not exceed the configured (or overridden) size limit.

    Checks Content-Length first for a fast-path rejection, then falls back to
    reading the full file if the header is absent or unreliable.
    Raises HTTPException 413 if the file is too large.
    Always seeks back to 0 after reading.
    """
    limit_mb = max_mb if max_mb is not None else settings.MAX_FILE_SIZE_MB
    limit_bytes = limit_mb * 1024 * 1024

    if file.size is not None and file.size > limit_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {file.size / (1024 * 1024):.1f} MB exceeds {limit_mb} MB limit.",
        )

    content = await file.read()
    size = len(content)
    await file.seek(0)

    if size > limit_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size / (1024 * 1024):.1f} MB exceeds {limit_mb} MB limit.",
        )


async def validate_pdf(file: UploadFile) -> str:
    """Validate that *file* is a PDF. Returns the detected MIME type."""
    await validate_file_size(file)
    return await validate_file_type(file, settings.ALLOWED_PDF_MIMES)


async def validate_image(file: UploadFile) -> str:
    """Validate that *file* is an allowed image format. Returns the detected MIME type."""
    await validate_file_size(file)
    return await validate_file_type(file, settings.ALLOWED_IMAGE_MIMES)
