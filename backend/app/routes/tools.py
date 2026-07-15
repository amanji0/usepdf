from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException, Depends
from typing import List, Optional
import json
import logging
from app.models import JobResponse
from app.services.storage import save_upload, save_uploads
from app.services.validation import validate_pdf, validate_image
from app.tasks import merge, split, rotate, compress, convert, security, office, edit
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tools", tags=["tools"])

def get_limiter(request: Request):
    return request.app.state.limiter

@router.post("/merge", response_model=JobResponse)
async def merge_pdfs(
    request: Request,
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
    
    task = merge.merge_pdfs.delay(file_paths)
    return JobResponse(job_id=task.id)

@router.post("/split", response_model=JobResponse)
async def split_pdf(
    request: Request,
    file: UploadFile = File(...),
    ranges: str = Form("all")
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    task = split.split_pdf.delay(str(path), ranges, file.filename)
    return JobResponse(job_id=task.id)

@router.post("/rotate", response_model=JobResponse)
async def rotate_pdf(
    request: Request,
    file: UploadFile = File(...),
    angle: int = Form(90),
    pages: Optional[str] = Form(None)
):
    await validate_pdf(file)
    if angle not in [90, 180, 270]:
        raise HTTPException(status_code=400, detail="Angle must be 90, 180, or 270")
    file_id, path = await save_upload(file)
    task = rotate.rotate_pdf.delay(str(path), angle, pages, file.filename)
    return JobResponse(job_id=task.id)

@router.post("/compress", response_model=JobResponse)
async def compress_pdf(
    request: Request,
    file: UploadFile = File(...),
    level: str = Form("recommended")
):
    await validate_pdf(file)
    if level not in ["low", "recommended", "extreme"]:
        raise HTTPException(status_code=400, detail="Invalid compression level")
    file_id, path = await save_upload(file)
    task = compress.compress_pdf.delay(str(path), level, file.filename)
    return JobResponse(job_id=task.id)

@router.post("/pdf-to-jpg", response_model=JobResponse)
async def pdf_to_jpg(
    request: Request,
    file: UploadFile = File(...),
    dpi: int = Form(150)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    task = convert.pdf_to_jpg.delay(str(path), dpi, file.filename)
    return JobResponse(job_id=task.id)

@router.post("/jpg-to-pdf", response_model=JobResponse)
async def jpg_to_pdf(
    request: Request,
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required")
    for f in files:
        await validate_image(f)
    saved = await save_uploads(files)
    file_paths = [str(p) for _, p in saved]
    task = convert.jpg_to_pdf.delay(file_paths)
    return JobResponse(job_id=task.id)

@router.post("/protect", response_model=JobResponse)
async def protect_pdf(
    request: Request,
    file: UploadFile = File(...),
    password: str = Form(...)
):
    await validate_pdf(file)
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    file_id, path = await save_upload(file)
    task = security.protect_pdf.delay(str(path), password, file.filename)
    return JobResponse(job_id=task.id)

@router.post("/unlock", response_model=JobResponse)
async def unlock_pdf(
    request: Request,
    file: UploadFile = File(...),
    password: str = Form(...)
):
    await validate_pdf(file)
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    file_id, path = await save_upload(file)
    task = security.unlock_pdf.delay(str(path), password, file.filename)
    return JobResponse(job_id=task.id)

@router.post("/pdf-to-word", response_model=JobResponse)
async def pdf_to_word(
    request: Request,
    file: UploadFile = File(...)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    task = office.pdf_to_word.delay(str(path), file.filename)
    return JobResponse(job_id=task.id)

@router.post("/pdf-to-powerpoint", response_model=JobResponse)
async def pdf_to_powerpoint(
    request: Request,
    file: UploadFile = File(...)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    task = office.pdf_to_powerpoint.delay(str(path), file.filename)
    return JobResponse(job_id=task.id)

@router.post("/pdf-to-excel", response_model=JobResponse)
async def pdf_to_excel(
    request: Request,
    file: UploadFile = File(...)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    task = office.pdf_to_excel.delay(str(path), file.filename)
    return JobResponse(job_id=task.id)

@router.post("/pdf-to-pages", response_model=JobResponse)
async def pdf_to_pages(
    request: Request,
    file: UploadFile = File(...)
):
    await validate_pdf(file)
    file_id, path = await save_upload(file)
    # Reuses the PDF to Word backend which produces a highly accurate .docx file for Apple Pages
    task = office.pdf_to_word.delay(str(path), file.filename)
    return JobResponse(job_id=task.id)

@router.post("/edit", response_model=JobResponse)
async def edit_pdf(
    request: Request,
    file: UploadFile = File(...),
    annotations: str = Form(...)
):
    await validate_pdf(file)
    try:
        anns = json.loads(annotations)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid annotations JSON")
    file_id, path = await save_upload(file)
    task = edit.add_text.delay(str(path), anns, file.filename)
    return JobResponse(job_id=task.id)
