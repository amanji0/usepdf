import subprocess
import logging
from pathlib import Path
from app.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

LEVEL_MAP = {
    'low': '/printer',
    'recommended': '/ebook',
    'extreme': '/screen',
}

@celery_app.task(bind=True, name='app.tasks.compress')
def compress_pdf(self, input_path: str, level: str = 'recommended', original_filename: str = 'document.pdf'):
    input_p = Path(input_path)
    output_p = settings.RESULT_DIR / f"{self.request.id}.pdf"
    
    gs_level = LEVEL_MAP.get(level, '/ebook')
    
    self.update_state(state='PROGRESS', meta={'progress': 10, 'filename': original_filename})
    
    try:
        cmd = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS={gs_level}',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_p}',
            str(input_p)
        ]
        
        logger.info(f"Running Ghostscript: {' '.join(cmd)}")
        subprocess.run(cmd, timeout=300, check=True)
        
        # Calculate compression ratio
        in_size = input_p.stat().st_size
        out_size = output_p.stat().st_size if output_p.exists() else 0
        ratio = (1 - (out_size / in_size)) * 100 if in_size > 0 else 0
        logger.info(f"Compressed {in_size} -> {out_size} bytes ({ratio:.1f}% reduction)")
        
        return {'result_path': str(output_p), 'filename': original_filename}
    except subprocess.TimeoutExpired:
        logger.error(f"Compression timed out for {input_p}")
        raise ValueError("Compression timed out")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ghostscript error: {e}")
        raise ValueError("Compression failed")
    except Exception as e:
        logger.error(f"Unexpected error in compress_pdf: {e}", exc_info=True)
        raise
