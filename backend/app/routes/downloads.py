from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.config import get_settings
from pathlib import Path

router = APIRouter(prefix="/api/download", tags=["downloads"])
settings = get_settings()

@router.get("/{job_id}")
async def download_result(job_id: str):
    res = AsyncResult(job_id, app=celery_app)
    if res.state != 'SUCCESS':
        raise HTTPException(status_code=400, detail="Job not complete")
        
    result_dict = res.info
    if not isinstance(result_dict, dict) or 'result_path' not in result_dict:
        raise HTTPException(status_code=500, detail="Invalid job result")
        
    path = Path(result_dict['result_path'])
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    filename = result_dict.get('filename', path.name)
    return FileResponse(
        path=path,
        filename=filename,
        content_disposition_type="attachment"
    )
