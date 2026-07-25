from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException, Depends, BackgroundTasks
from app.job_manager import create_job, run_task
from app.celery_app import FakeTaskContext
from typing import List, Optional
import json
import logging
from app.models import JobResponse
from app.services.storage import save_upload, save_uploads
from app.services.validation import validate_pdf, validate_image
from app.tasks import merge, split, rotate, compress, convert, security, office, edit, advanced, intelligence
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tools", tags=["tools"])

def get_limiter(request: Request):
    return request.app.state.limiter

@router.post("/merge", response_model=JobResponse)
async def merge_pdfs(
    request: Request,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    order: Optional[str] = Form(None)
):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Merge requires at least 2 files")
    for f in files:
        await validate_pdf(f)
    
    # Process order if provided, but for now we just take the order they are in
    saved = await save_uploads(files)
    file_paths = [str(p) for _, p in saved]
    
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, merge.merge_pdfs, FakeTaskContext(job_id), file_paths)
    return JobResponse(job_id=job_id)

@router.post("/split", response_model=JobResponse)
async def split_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    ranges: str = Form("all")
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, split.split_pdf, FakeTaskContext(job_id), str(path), ranges, file.filename)
    return JobResponse(job_id=job_id)

@router.post("/rotate", response_model=JobResponse)
async def rotate_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    angle: int = Form(90),
    pages: Optional[str] = Form(None)
):
    await validate_pdf(file)
    if angle not in [90, 180, 270]:
        raise HTTPException(status_code=400, detail="Angle must be 90, 180, or 270")
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, rotate.rotate_pdf, FakeTaskContext(job_id), str(path), angle, pages, file.filename)
    return JobResponse(job_id=job_id)

@router.post("/compress", response_model=JobResponse)
async def compress_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    level: str = Form("recommended")
):
    await validate_pdf(file)
    if level not in ["low", "recommended", "extreme"]:
        raise HTTPException(status_code=400, detail="Invalid compression level")
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, compress.compress_pdf, FakeTaskContext(job_id), str(path), level, file.filename)
    return JobResponse(job_id=job_id)

@router.post("/pdf-to-jpg", response_model=JobResponse)
async def pdf_to_jpg(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    dpi: int = Form(150)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, convert.pdf_to_jpg, FakeTaskContext(job_id), str(path), dpi, file.filename)
    return JobResponse(job_id=job_id)

@router.post("/jpg-to-pdf", response_model=JobResponse)
async def jpg_to_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required")
    for f in files:
        await validate_image(f)
    saved = await save_uploads(files)
    file_paths = [str(p) for _, p in saved]
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, convert.jpg_to_pdf, FakeTaskContext(job_id), file_paths)
    return JobResponse(job_id=job_id)

@router.post("/protect", response_model=JobResponse)
async def protect_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    password: str = Form(...)
):
    await validate_pdf(file)
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, security.protect_pdf, FakeTaskContext(job_id), str(path), password, file.filename)
    return JobResponse(job_id=job_id)

@router.post("/unlock", response_model=JobResponse)
async def unlock_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    password: str = Form(...)
):
    await validate_pdf(file)
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, security.unlock_pdf, FakeTaskContext(job_id), str(path), password, file.filename)
    return JobResponse(job_id=job_id)

@router.post("/pdf-to-word", response_model=JobResponse)
async def pdf_to_word(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, office.pdf_to_word, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/pdf-to-powerpoint", response_model=JobResponse)
async def pdf_to_powerpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, office.pdf_to_powerpoint, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/pdf-to-excel", response_model=JobResponse)
async def pdf_to_excel(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, office.pdf_to_excel, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/pdf-to-pages", response_model=JobResponse)
async def pdf_to_pages(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    # Reuses the PDF to Word backend which produces a highly accurate .docx file for Apple Pages
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, office.pdf_to_word, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/edit", response_model=JobResponse)
async def edit_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    annotations: str = Form(...)
):
    await validate_pdf(file)
    try:
        anns = json.loads(annotations)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid annotations JSON")
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, edit.add_text, FakeTaskContext(job_id), str(path), anns, file.filename)
    return JobResponse(job_id=job_id)

# --- NEW ADVANCED ROUTES ---

@router.post("/remove-pages", response_model=JobResponse)
async def remove_pages(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...), pages: str = Form("")):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.remove_pages, FakeTaskContext(job_id), str(path), pages, file.filename)
    return JobResponse(job_id=job_id)

@router.post("/extract-pages", response_model=JobResponse)
async def extract_pages(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...), pages: str = Form("")):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.extract_pages, FakeTaskContext(job_id), str(path), pages, file.filename)
    return JobResponse(job_id=job_id)

@router.post("/organize-pdf", response_model=JobResponse)
async def organize_pdf(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.organize_pdf, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/scan-to-pdf", response_model=JobResponse)
async def scan_to_pdf(request: Request, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    for f in files:
        await validate_image(f)
    saved = await save_uploads(files)
    file_paths = [str(p) for _, p in saved]
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.scan_to_pdf, FakeTaskContext(job_id), file_paths)
    return JobResponse(job_id=job_id)

@router.post("/repair-pdf", response_model=JobResponse)
async def repair_pdf(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.repair_pdf, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/ocr-pdf", response_model=JobResponse)
async def ocr_pdf(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.ocr_pdf, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/word-to-pdf", response_model=JobResponse)
async def word_to_pdf(request: Request, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    saved = await save_uploads(files)
    file_paths = [str(p) for _, p in saved]
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.word_to_pdf, FakeTaskContext(job_id), file_paths)
    return JobResponse(job_id=job_id)

@router.post("/powerpoint-to-pdf", response_model=JobResponse)
async def powerpoint_to_pdf(request: Request, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    saved = await save_uploads(files)
    file_paths = [str(p) for _, p in saved]
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.powerpoint_to_pdf, FakeTaskContext(job_id), file_paths)
    return JobResponse(job_id=job_id)

@router.post("/excel-to-pdf", response_model=JobResponse)
async def excel_to_pdf(request: Request, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    saved = await save_uploads(files)
    file_paths = [str(p) for _, p in saved]
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.excel_to_pdf, FakeTaskContext(job_id), file_paths)
    return JobResponse(job_id=job_id)

@router.post("/html-to-pdf", response_model=JobResponse)
async def html_to_pdf(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.html_to_pdf, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/pdf-to-pdfa", response_model=JobResponse)
async def pdf_to_pdfa(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.pdf_to_pdfa, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/add-page-numbers", response_model=JobResponse)
async def add_page_numbers(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.add_page_numbers, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/add-watermark", response_model=JobResponse)
async def add_watermark(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.add_watermark, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/crop-pdf", response_model=JobResponse)
async def crop_pdf(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.crop_pdf, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/pdf-forms", response_model=JobResponse)
async def pdf_forms(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.pdf_forms, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/sign-pdf", response_model=JobResponse)
async def sign_pdf(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.sign_pdf, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/redact-pdf", response_model=JobResponse)
async def redact_pdf(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.redact_pdf, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/compare-pdf", response_model=JobResponse)
async def compare_pdf(request: Request, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    if len(files) != 2:
        raise HTTPException(status_code=400, detail="Compare requires exactly 2 files")
    for f in files:
        await validate_pdf(f)
    saved = await save_uploads(files)
    file_paths = [str(p) for _, p in saved]
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, advanced.compare_pdf, FakeTaskContext(job_id), file_paths)
    return JobResponse(job_id=job_id)

# --- INTELLIGENCE ROUTES ---

@router.post("/ai-summarizer", response_model=JobResponse)
async def ai_summarizer(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, intelligence.ai_summarize, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/translate-pdf", response_model=JobResponse)
async def translate_pdf(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, intelligence.translate_pdf, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/pdf-to-markdown", response_model=JobResponse)
async def pdf_to_markdown(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, intelligence.pdf_to_markdown, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)

@router.post("/doc-talk", response_model=JobResponse)
async def doc_talk(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    job_id = create_job()
    background_tasks.add_task(run_task, job_id, intelligence.doc_talk, FakeTaskContext(job_id), str(path), file.filename)
    return JobResponse(job_id=job_id)
