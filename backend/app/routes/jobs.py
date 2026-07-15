from fastapi import APIRouter
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.models import JobStatus
from app.services.storage import get_result_url

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    res = AsyncResult(job_id, app=celery_app)
    
    status_map = {
        'PENDING': 'queued',
        'STARTED': 'processing',
        'PROGRESS': 'processing',
        'SUCCESS': 'done',
        'FAILURE': 'error'
    }
    
    status = status_map.get(res.state, 'error')
    progress = None
    download_url = None
    error_msg = None
    filename = None
    
    if res.state == 'PROGRESS' and isinstance(res.info, dict):
        progress = res.info.get('progress')
        filename = res.info.get('filename')
    elif res.state == 'SUCCESS' and isinstance(res.info, dict):
        download_url = get_result_url(job_id)
        filename = res.info.get('filename')
        progress = 100
    elif res.state == 'FAILURE':
        error_msg = str(res.info)
        
    return JobStatus(
        job_id=job_id,
        status=status,
        progress=progress,
        download_url=download_url,
        error=error_msg,
        filename=filename
    )
