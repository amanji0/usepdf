from pypdf import PdfReader, PdfWriter
import logging
from pathlib import Path
from app.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

@celery_app.task(bind=True, name='app.tasks.protect')
def protect_pdf(self, input_path: str, password: str, original_filename: str = 'document.pdf'):
    input_p = Path(input_path)
    output_p = settings.RESULT_DIR / f"{self.request.id}.pdf"
    stem = Path(original_filename).stem
    out_name = f"{stem}_protected.pdf"
    
    self.update_state(state='PROGRESS', meta={'progress': 10, 'filename': out_name})
    
    try:
        reader = PdfReader(str(input_p))
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        writer.encrypt(password, algorithm='AES-256')
        with open(output_p, 'wb') as f:
            writer.write(f)
            
        return {'result_path': str(output_p), 'filename': out_name}
    except Exception as e:
        logger.error(f"Error in protect_pdf: {e}", exc_info=True)
        raise

@celery_app.task(bind=True, name='app.tasks.unlock')
def unlock_pdf(self, input_path: str, password: str, original_filename: str = 'document.pdf'):
    input_p = Path(input_path)
    output_p = settings.RESULT_DIR / f"{self.request.id}.pdf"
    stem = Path(original_filename).stem
    out_name = f"{stem}_unlocked.pdf"
    
    self.update_state(state='PROGRESS', meta={'progress': 10, 'filename': out_name})
    
    try:
        reader = PdfReader(str(input_p))
        if not reader.is_encrypted:
            raise ValueError("PDF is not encrypted")
            
        success = reader.decrypt(password)
        if not success:
            raise ValueError("Incorrect password")
            
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
            
        with open(output_p, 'wb') as f:
            writer.write(f)
            
        return {'result_path': str(output_p), 'filename': out_name}
    except Exception as e:
        logger.error(f"Error in unlock_pdf: {e}", exc_info=True)
        raise
