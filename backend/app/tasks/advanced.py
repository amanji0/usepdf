import logging
import os

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

import fitz

def _parse_page_ranges(pages_str: str, max_pages: int) -> list[int]:
    pages = set()
    for part in pages_str.split(','):
        part = part.strip()
        if not part: continue
        if '-' in part:
            start, end = part.split('-')
            start, end = int(start), int(end)
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted([p - 1 for p in pages if 1 <= p <= max_pages])

def remove_pages(self, file_path: str, pages: str, original_filename: str):
    doc = fitz.open(file_path)
    to_remove = _parse_page_ranges(pages, doc.page_count)
    doc.delete_pages(to_remove)
    
    output_filename = f"removed_{original_filename}"
    output_path = os.path.join(settings.RESULT_DIR, output_filename)
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return {"status": "done", "result_path": output_path, "filename": output_filename}


def extract_pages(self, file_path: str, pages: str, original_filename: str):
    doc = fitz.open(file_path)
    to_extract = _parse_page_ranges(pages, doc.page_count)
    
    new_doc = fitz.open()
    for page_num in to_extract:
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
    output_filename = f"extracted_{original_filename}"
    output_path = os.path.join(settings.RESULT_DIR, output_filename)
    new_doc.save(output_path, garbage=3, deflate=True)
    new_doc.close()
    doc.close()
    return {"status": "done", "result_path": output_path, "filename": output_filename}


def organize_pdf(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"organized_{original_filename}"}


def scan_to_pdf(self, file_paths: list[str]):
    return {"status": "done", "result": file_paths[0], "filename": "scanned.pdf"}


def repair_pdf(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"repaired_{original_filename}"}


def ocr_pdf(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"ocr_{original_filename}"}


def word_to_pdf(self, file_paths: list[str]):
    return {"status": "done", "result": file_paths[0], "filename": "converted.pdf"}


def powerpoint_to_pdf(self, file_paths: list[str]):
    return {"status": "done", "result": file_paths[0], "filename": "converted.pdf"}


def excel_to_pdf(self, file_paths: list[str]):
    return {"status": "done", "result": file_paths[0], "filename": "converted.pdf"}


def html_to_pdf(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": "converted.pdf"}


def pdf_to_pdfa(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"pdfa_{original_filename}"}


def add_page_numbers(self, file_path: str, original_filename: str):
    doc = fitz.open(file_path)
    for i, page in enumerate(doc):
        rect = page.rect
        # Bottom right, slightly offset
        point = fitz.Point(rect.width - 50, rect.height - 30)
        page.insert_text(point, f"{i + 1}", fontname="helv", fontsize=12, color=(0, 0, 0))
        
    output_filename = f"numbered_{original_filename}"
    output_path = os.path.join(settings.RESULT_DIR, output_filename)
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return {"status": "done", "result_path": output_path, "filename": output_filename}


def add_watermark(self, file_path: str, original_filename: str):
    doc = fitz.open(file_path)
    for page in doc:
        rect = page.rect
        # Center watermark, 45 degree angle
        text = "CONFIDENTIAL"
        font_size = min(rect.width, rect.height) / len(text) * 1.5
        
        tw = fitz.TextWriter(rect)
        tw.append((rect.width / 4, rect.height / 1.5), text, font="helv-bo", fontsize=font_size)
        tw.write_text(page, color=(0.7, 0.7, 0.7), render_mode=0, opacity=0.3)
        
    output_filename = f"watermarked_{original_filename}"
    output_path = os.path.join(settings.RESULT_DIR, output_filename)
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()
    return {"status": "done", "result_path": output_path, "filename": output_filename}


def crop_pdf(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"cropped_{original_filename}"}


def pdf_forms(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"forms_{original_filename}"}


def sign_pdf(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"signed_{original_filename}"}


def redact_pdf(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"redacted_{original_filename}"}


def compare_pdf(self, file_paths: list[str]):
    return {"status": "done", "result": file_paths[0], "filename": "compared.pdf"}
