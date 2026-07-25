from fastapi import APIRouter
from app.job_manager import get_job_status as get_job_state
from app.models import JobStatus
from app.services.storage import get_result_url

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    job = get_job_state(job_id)
    
    state = job.get('status', 'error')
    status_map = {
        'pending': 'queued',
        'processing': 'processing',
        'PROGRESS': 'processing',
        'completed': 'done',
        'error': 'error'
    }
    
    status = status_map.get(state, 'error')
    progress = job.get('progress', None)
    error_msg = job.get('error', None)
    
    # We don't have filename in job state easily, but we can return None or derive it
    filename = job.get('filename', None)
    download_url = None
    
    if status == 'done':
        download_url = get_result_url(job_id)
        progress = 100
        
    return JobStatus(
        job_id=job_id,
        status=status,
        progress=progress,
        download_url=download_url,
        error=error_msg,
        filename=filename
    )
