from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.job_manager import get_job_status
from app.config import get_settings
from pathlib import Path

router = APIRouter(prefix="/api/download", tags=["downloads"])
settings = get_settings()

@router.get("/{job_id}")
async def download_result(job_id: str):
    job = get_job_status(job_id)
    if job.get('status') != 'completed':
        raise HTTPException(status_code=400, detail="Job not complete")
        
    result_path = job.get('result')
    if not result_path:
        raise HTTPException(status_code=500, detail="Invalid job result")
        
    path = Path(result_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    filename = job.get('filename', path.name)
    return FileResponse(
        path=path,
        filename=filename,
        content_disposition_type="attachment"
    )
