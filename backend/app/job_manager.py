import asyncio
import uuid
from typing import Dict, Any

# Simple in-memory state manager for background tasks
# Note: In a free serverless environment (like Render), 
# this memory is wiped when the container sleeps/restarts.
# But it solves the problem for active processing sessions without Redis.

_jobs: Dict[str, Dict[str, Any]] = {}

def create_job() -> str:
    """Create a new job and return its ID."""
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "progress": 0}
    return job_id

def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get the status of a specific job."""
    if job_id not in _jobs:
        return {"status": "error", "error": "Job not found."}
    return _jobs[job_id]

def update_job(job_id: str, status: str, progress: int = None, result: str = None, error: str = None, filename: str = None):
    """Update a job's status."""
    if job_id in _jobs:
        _jobs[job_id]["status"] = status
        if progress is not None:
            _jobs[job_id]["progress"] = progress
        if result is not None:
            _jobs[job_id]["result"] = result
        if error is not None:
            _jobs[job_id]["error"] = error
        if filename is not None:
            _jobs[job_id]["filename"] = filename

async def run_task(job_id: str, func, *args, **kwargs):
    """Run a synchronous task function in a separate thread and manage its job state."""
    loop = asyncio.get_running_loop()
    
    update_job(job_id, status="processing", progress=10)
    
    try:
        # Run blocking synchronous functions in the default executor (thread pool)
        # We assume the task function returns a dictionary or path representing the result
        result = await loop.run_in_executor(None, func, *args, **kwargs)
        
        if isinstance(result, dict) and "error" in result:
             update_job(job_id, status="error", error=result["error"])
        elif isinstance(result, dict):
             update_job(job_id, status="completed", progress=100, 
                        result=result.get("result_path"), 
                        filename=result.get("filename"))
        elif isinstance(result, str):
             update_job(job_id, status="completed", progress=100, result=result)
        else:
             update_job(job_id, status="completed", progress=100)
    except Exception as e:
        update_job(job_id, status="error", error=str(e))
