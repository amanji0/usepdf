import fitz
import logging
from pathlib import Path
from typing import List, Dict

from app.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.edit.add_text")
def add_text(self, input_path: str, annotations: List[Dict], original_filename: str):
    """
    annotations format: [{"page": int, "text": str, "x_pct": float, "y_pct": float, "size": int}]
    """
    try:
        input_p = Path(input_path)
        output_dir = Path(get_settings().RESULT_DIR) / self.request.id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        out_filename = f"edited_{original_filename}"
        output_p = output_dir / out_filename
        
        doc = fitz.open(input_path)
        
        # apply annotations
        for index, ann in enumerate(annotations):
            page_idx = ann.get("page", 1) - 1
            if page_idx < 0 or page_idx >= len(doc):
                continue
            
            page = doc[page_idx]
            page_rect = page.rect
            x = page_rect.width * ann.get("x_pct", 0)
            y = page_rect.height * ann.get("y_pct", 0)
            
            ann_type = ann.get("type", "text")
            
            if ann_type == "rect":
                w = page_rect.width * ann.get("width_pct", 0.1)
                h = page_rect.height * ann.get("height_pct", 0.05)
                # Draw white rectangle
                shape = page.new_shape()
                shape.draw_rect(fitz.Rect(x, y, x + w, y + h))
                shape.finish(color=(1, 1, 1), fill=(1, 1, 1))
                shape.commit()
            else:
                # insert text
                text = ann.get("text", "")
                size = ann.get("size", 12)
                
                # In Fabric JS, text Y coordinate is top-left, but PyMuPDF point is bottom-left usually depending on descender.
                # Adding size offset so it roughly matches what user saw on screen.
                p = fitz.Point(x, y + (size * 0.75))
                page.insert_text(p, text, fontsize=size, color=(0,0,0))
            
            # Progress update
            self.update_state(state='PROGRESS', meta={'progress': int(((index + 1) / len(annotations)) * 100)})

        doc.save(str(output_p))
        doc.close()
        
        return {
            "status": "success",
            "file_url": f"/api/v1/downloads/{self.request.id}/{out_filename}"
        }
    except Exception as e:
        logger.error(f"Error adding text to PDF: {str(e)}")
        raise e
