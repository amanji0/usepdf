import pymupdf
import img2pdf
import zipfile
import logging
from pathlib import Path
from app.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

@celery_app.task(bind=True, name='app.tasks.pdf_to_jpg')
def pdf_to_jpg(self, input_path: str, dpi: int = 150, original_filename: str = 'document.pdf'):
    input_p = Path(input_path)
    stem = Path(original_filename).stem
    
    try:
        doc = pymupdf.open(str(input_p))
        total = len(doc)
        
        if total == 0:
            raise ValueError("PDF has no pages")
            
        if total == 1:
            page = doc[0]
            pix = page.get_pixmap(dpi=dpi)
            output_p = settings.RESULT_DIR / f"{self.request.id}.jpg"
            pix.save(str(output_p))
            return {'result_path': str(output_p), 'filename': f"{stem}.jpg"}
            
        # Multi-page: create a zip
        zip_path = settings.RESULT_DIR / f"{self.request.id}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for i in range(total):
                page = doc[i]
                pix = page.get_pixmap(dpi=dpi)
                temp_jpg = settings.RESULT_DIR / f"{self.request.id}_{i}.jpg"
                pix.save(str(temp_jpg))
                zf.write(temp_jpg, arcname=f"{stem}_page_{i+1}.jpg")
                temp_jpg.unlink() # Cleanup temp
                
                prog = int(((i + 1) / total) * 100)
                self.update_state(state='PROGRESS', meta={'progress': prog, 'filename': f"{stem}.zip"})
                
        doc.close()
        return {'result_path': str(zip_path), 'filename': f"{stem}.zip"}
    except Exception as e:
        logger.error(f"Error in pdf_to_jpg: {e}", exc_info=True)
        raise

@celery_app.task(bind=True, name='app.tasks.jpg_to_pdf')
def jpg_to_pdf(self, input_paths: list[str], output_filename: str = 'images.pdf'):
    try:
        output_p = settings.RESULT_DIR / f"{self.request.id}.pdf"
        self.update_state(state='PROGRESS', meta={'progress': 50, 'filename': output_filename})
        
        pdf_bytes = img2pdf.convert(input_paths)
        with open(output_p, 'wb') as f:
            f.write(pdf_bytes)
            
        return {'result_path': str(output_p), 'filename': output_filename}
    except Exception as e:
        logger.error(f"Error in jpg_to_pdf: {e}", exc_info=True)
        raise
