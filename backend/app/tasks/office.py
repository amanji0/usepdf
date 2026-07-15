import logging
from pathlib import Path

from app.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.pdf_to_word")
def pdf_to_word(self, input_path: str, original_filename: str = "document.pdf") -> dict:
    settings = get_settings()
    stem = Path(original_filename).stem
    output_path = settings.RESULT_DIR / f"{self.request.id}.docx"
    
    logger.info("Converting %s to DOCX", original_filename)
    
    try:
        from pdf2docx import Converter
        
        cv = Converter(input_path)
        self.update_state(state="PROGRESS", meta={"progress": 50, "filename": f"{stem}.docx"})
        
        cv.convert(str(output_path), start=0, end=None)
        cv.close()
        
        return {"result_path": str(output_path), "filename": f"{stem}.docx"}
    except Exception:
        logger.exception("Error converting PDF to Word")
        raise


@celery_app.task(bind=True, name="app.tasks.pdf_to_powerpoint")
def pdf_to_powerpoint(self, input_path: str, original_filename: str = "document.pdf") -> dict:
    settings = get_settings()
    stem = Path(original_filename).stem
    output_path = settings.RESULT_DIR / f"{self.request.id}.pptx"
    
    logger.info("Converting %s to PPTX", original_filename)
    
    try:
        import pymupdf
        from pptx import Presentation
        from pptx.util import Inches
        
        doc = pymupdf.open(input_path)
        prs = Presentation()
        blank_slide_layout = prs.slide_layouts[6] 
        
        total = len(doc)
        if total == 0:
            raise ValueError("PDF has no pages")
            
        for i in range(total):
            page = doc[i]
            pix = page.get_pixmap(dpi=150)
            temp_img_path = settings.RESULT_DIR / f"{self.request.id}_page_{i}.png"
            pix.save(str(temp_img_path))
            
            if i == 0:
                prs.slide_width = int(page.rect.width * 12700)
                prs.slide_height = int(page.rect.height * 12700)
            
            slide = prs.slides.add_slide(blank_slide_layout)
            slide.shapes.add_picture(str(temp_img_path), 0, 0, width=prs.slide_width, height=prs.slide_height)
            
            temp_img_path.unlink()
            
            progress = int(((i + 1) / total) * 100)
            self.update_state(state="PROGRESS", meta={"progress": progress, "filename": f"{stem}.pptx"})
            
        prs.save(str(output_path))
        doc.close()
        
        return {"result_path": str(output_path), "filename": f"{stem}.pptx"}
    except Exception:
        logger.exception("Error converting PDF to PPTX")
        raise


@celery_app.task(bind=True, name="app.tasks.pdf_to_excel")
def pdf_to_excel(self, input_path: str, original_filename: str = "document.pdf") -> dict:
    settings = get_settings()
    stem = Path(original_filename).stem
    output_path = settings.RESULT_DIR / f"{self.request.id}.xlsx"
    
    logger.info("Converting %s to XLSX", original_filename)
    
    try:
        import pdfplumber
        from openpyxl import Workbook
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Extracted Tables"
        
        row_offset = 1
        with pdfplumber.open(input_path) as pdf:
            total = len(pdf.pages)
            if total == 0:
                raise ValueError("PDF has no pages")
                
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        clean_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        for col_idx, cell_value in enumerate(clean_row, start=1):
                            ws.cell(row=row_offset, column=col_idx, value=cell_value)
                        row_offset += 1
                    # Add a blank row between tables
                    row_offset += 1
                
                progress = int(((i + 1) / total) * 100)
                self.update_state(state="PROGRESS", meta={"progress": progress, "filename": f"{stem}.xlsx"})
                
        # If no tables found, at least return an empty excel sheet rather than failing completely
        wb.save(str(output_path))
        
        return {"result_path": str(output_path), "filename": f"{stem}.xlsx"}
    except Exception:
        logger.exception("Error converting PDF to Excel")
        raise
