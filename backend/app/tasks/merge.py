"""
Merge multiple PDF files into a single PDF.

Uses pypdf's PdfWriter.append() for reliable, lossless merging.
"""

import logging
from pathlib import Path

from pypdf import PdfWriter

from app.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.merge")
def merge_pdfs(
    self,
    input_paths: list[str],
    output_filename: str = "merged.pdf",
) -> dict:
    """Merge multiple PDFs into one.

    Args:
        input_paths: List of absolute file-path strings to merge (in order).
        output_filename: Desired filename for the merged result.

    Returns:
        dict with ``result_path`` and ``filename``.
    """
    settings = get_settings()
    result_dir = Path(settings.RESULT_DIR)
    result_dir.mkdir(parents=True, exist_ok=True)

    output_path = result_dir / f"{self.request.id}.pdf"
    total = len(input_paths)

    logger.info("Starting merge of %d PDFs -> %s", total, output_filename)

    try:
        writer = PdfWriter()

        for idx, raw_path in enumerate(input_paths, start=1):
            file_path = Path(raw_path)
            if not file_path.is_file():
                raise FileNotFoundError(f"Input file not found: {file_path}")

            logger.debug("Appending %s (%d/%d)", file_path.name, idx, total)
            writer.append(str(file_path))

            progress = int((idx / total) * 100)
            self.update_state(
                state="PROGRESS",
                meta={"progress": progress, "filename": output_filename},
            )

        with open(output_path, "wb") as fh:
            writer.write(fh)

        writer.close()

        logger.info("Merge complete: %s (%d bytes)", output_path, output_path.stat().st_size)

        return {"result_path": str(output_path), "filename": output_filename}

    except FileNotFoundError:
        logger.exception("Input file missing during merge")
        raise
    except Exception:
        logger.exception("Unexpected error during PDF merge")
        raise
