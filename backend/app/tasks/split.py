"""
Split a PDF by page ranges or extract every page individually.

Supports range syntax like ``1-3,5,7-9`` and the special value ``all``
to extract every page as a separate single-page PDF bundled in a zip.
"""

import logging
import zipfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)


def parse_ranges(ranges_str: str, total_pages: int) -> list[list[int]]:
    """Parse a human-friendly range string into groups of 0-based page indices.

    Args:
        ranges_str: Comma-separated ranges, e.g. ``"1-3,5,7-9"``.
            Page numbers are **1-based** (user-facing).
        total_pages: Total number of pages in the source PDF.

    Returns:
        A list of lists, where each inner list is one contiguous group of
        0-based page indices.  E.g. ``[[0,1,2], [4], [6,7,8]]``.

    Raises:
        ValueError: If the string contains invalid tokens or out-of-range pages.
    """
    groups: list[list[int]] = []

    for part in ranges_str.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            tokens = part.split("-", maxsplit=1)
            if len(tokens) != 2 or not tokens[0].strip() or not tokens[1].strip():
                raise ValueError(f"Invalid range format: '{part}'")

            try:
                start = int(tokens[0].strip())
                end = int(tokens[1].strip())
            except ValueError:
                raise ValueError(f"Non-numeric value in range: '{part}'")

            if start < 1 or end < 1:
                raise ValueError(f"Page numbers must be >= 1, got: '{part}'")
            if start > end:
                raise ValueError(f"Start page cannot exceed end page: '{part}'")
            if end > total_pages:
                raise ValueError(
                    f"Page {end} exceeds document length ({total_pages} pages)"
                )

            groups.append(list(range(start - 1, end)))  # convert to 0-based
        else:
            try:
                page_num = int(part)
            except ValueError:
                raise ValueError(f"Non-numeric page number: '{part}'")

            if page_num < 1:
                raise ValueError(f"Page numbers must be >= 1, got: {page_num}")
            if page_num > total_pages:
                raise ValueError(
                    f"Page {page_num} exceeds document length ({total_pages} pages)"
                )

            groups.append([page_num - 1])  # convert to 0-based

    if not groups:
        raise ValueError("No valid page ranges provided")

    return groups


@celery_app.task(bind=True, name="app.tasks.split")
def split_pdf(
    self,
    input_path: str,
    ranges: str,
    original_filename: str = "document.pdf",
) -> dict:
    """Split a PDF by page ranges.

    Args:
        input_path: Absolute path to the source PDF.
        ranges: Page range string (e.g. ``"1-3,5,7-9"``) or ``"all"``.
        original_filename: Original upload filename (used for output naming).

    Returns:
        dict with ``result_path`` and ``filename``.
    """
    settings = get_settings()
    result_dir = Path(settings.RESULT_DIR)
    result_dir.mkdir(parents=True, exist_ok=True)

    file_path = Path(input_path)
    stem = Path(original_filename).stem
    task_id = self.request.id

    logger.info("Starting split: %s, ranges=%s", original_filename, ranges)

    try:
        reader = PdfReader(str(file_path))
        total_pages = len(reader.pages)

        if total_pages == 0:
            raise ValueError("PDF has no pages")

        # --- Determine page groups ------------------------------------------
        if ranges.strip().lower() == "all":
            groups = [[i] for i in range(total_pages)]
        else:
            groups = parse_ranges(ranges, total_pages)

        # --- Single group → single PDF; multiple groups → zip ----------------
        if len(groups) == 1 and ranges.strip().lower() != "all":
            # Output a single PDF
            writer = PdfWriter()
            for page_idx in groups[0]:
                writer.add_page(reader.pages[page_idx])

            output_path = result_dir / f"{task_id}.pdf"
            with open(output_path, "wb") as fh:
                writer.write(fh)
            writer.close()

            range_label = ranges.strip().replace(",", "_")
            output_filename = f"{stem}_pages_{range_label}.pdf"

            self.update_state(
                state="PROGRESS",
                meta={"progress": 100, "filename": output_filename},
            )

            logger.info("Split complete (single PDF): %s", output_path)
            return {"result_path": str(output_path), "filename": output_filename}

        # Multiple groups or "all" → zip
        zip_path = result_dir / f"{task_id}.zip"
        output_filename = f"{stem}_split.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for group_idx, page_indices in enumerate(groups, start=1):
                writer = PdfWriter()
                for page_idx in page_indices:
                    writer.add_page(reader.pages[page_idx])

                # Name individual PDFs inside the zip
                if len(page_indices) == 1:
                    inner_name = f"{stem}_page_{page_indices[0] + 1}.pdf"
                else:
                    start = page_indices[0] + 1
                    end = page_indices[-1] + 1
                    inner_name = f"{stem}_pages_{start}-{end}.pdf"

                # Write to a temporary bytes buffer
                from io import BytesIO

                buf = BytesIO()
                writer.write(buf)
                writer.close()
                zf.writestr(inner_name, buf.getvalue())

                progress = int((group_idx / len(groups)) * 100)
                self.update_state(
                    state="PROGRESS",
                    meta={"progress": progress, "filename": output_filename},
                )

        logger.info("Split complete (zip): %s", zip_path)
        return {"result_path": str(zip_path), "filename": output_filename}

    except ValueError:
        logger.exception("Invalid range or PDF during split")
        raise
    except Exception:
        logger.exception("Unexpected error during PDF split")
        raise
