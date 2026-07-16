import logging
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def ai_summarize(self, file_path: str, original_filename: str):
    # Dummy implementation for AI summarizer
    return {"status": "done", "result": file_path, "filename": f"summary_{original_filename}"}

@shared_task(bind=True)
def translate_pdf(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"translated_{original_filename}"}

@shared_task(bind=True)
def pdf_to_markdown(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"markdown_{original_filename}"}

@shared_task(bind=True)
def doc_talk(self, file_path: str, original_filename: str):
    return {"status": "done", "result": file_path, "filename": f"doctalk_{original_filename}"}
