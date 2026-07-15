"""
Rotate selected (or all) pages of a PDF by a given angle.

Uses pypdf's ``page.rotate()`` which applies a clockwise rotation of
90, 180, or 270 degrees.
"""

import logging
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)

VALID_ANGLES = {90, 180, 270}


@celery_app.task(bind=True, name="app.tasks.rotate")
def rotate_pdf(
    self,
    input_path: str,
    angle: int,
    pages: str | None = None,
    original_filename: str = "document.pdf",
) -> dict:
    """Rotate pages of a PDF.

    Args:
        input_path: Absolute path to the source PDF.
        angle: Rotation angle — must be 90, 180, or 270 (clockwise).
        pages: Comma-separated 1-based page numbers to rotate, or ``None``
            to rotate every page.
        original_filename: Original upload filename (used for output naming).

    Returns:
        dict with ``result_path`` and ``filename``.
    """
    settings = get_settings()
    result_dir = Path(settings.RESULT_DIR)
    result_dir.mkdir(parents=True, exist_ok=True)

    file_path = Path(input_path)
    stem = Path(original_filename).stem
    suffix = Path(original_filename).suffix or ".pdf"
    output_path = result_dir / f"{self.request.id}.pdf"
    output_filename = f"{stem}_rotated{suffix}"

    logger.info(
        "Starting rotate: %s, angle=%d, pages=%s",
        original_filename,
        angle,
        pages or "all",
    )

    try:
        if angle not in VALID_ANGLES:
            raise ValueError(
                f"Invalid rotation angle: {angle}. Must be one of {sorted(VALID_ANGLES)}."
            )

        reader = PdfReader(str(file_path))
        total_pages = len(reader.pages)

        if total_pages == 0:
            raise ValueError("PDF has no pages")

        # Determine which pages to rotate (0-based set)
        if pages is None:
            rotate_indices: set[int] = set(range(total_pages))
        else:
            rotate_indices = set()
            for token in pages.split(","):
                token = token.strip()
                if not token:
                    continue
                try:
                    page_num = int(token)
                except ValueError:
                    raise ValueError(f"Non-numeric page number: '{token}'")

                if page_num < 1 or page_num > total_pages:
                    raise ValueError(
                        f"Page {page_num} out of range (1-{total_pages})"
                    )
                rotate_indices.add(page_num - 1)

        writer = PdfWriter()

        for idx in range(total_pages):
            page = reader.pages[idx]
            if idx in rotate_indices:
                page.rotate(angle)
            writer.add_page(page)

            progress = int(((idx + 1) / total_pages) * 100)
            self.update_state(
                state="PROGRESS",
                meta={"progress": progress, "filename": output_filename},
            )

        with open(output_path, "wb") as fh:
            writer.write(fh)

        writer.close()

        logger.info("Rotate complete: %s (%d bytes)", output_path, output_path.stat().st_size)

        return {"result_path": str(output_path), "filename": output_filename}

    except ValueError:
        logger.exception("Validation error during rotate")
        raise
    except Exception:
        logger.exception("Unexpected error during PDF rotate")
        raise
