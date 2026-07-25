from typing import Callable
from app.job_manager import update_job

class FakeRequest:
    def __init__(self, job_id: str):
        self.id = job_id

class FakeTaskContext:
    """Mock Celery task context injected as `self` into bound tasks."""
    def __init__(self, job_id: str):
        self.request = FakeRequest(job_id)

    def update_state(self, state: str, meta: dict = None):
        if meta and 'progress' in meta:
            update_job(self.request.id, status=state, progress=meta['progress'])
        else:
            update_job(self.request.id, status=state)

class FakeCelery:
    """Mock Celery app to keep task decorators happy without actually running Celery."""
    def task(self, bind=False, name=None):
        def decorator(func: Callable):
            # In our setup, we just return the original function.
            # We will manually pass `FakeTaskContext` as the first argument when calling it from routes.
            return func
        return decorator

celery_app = FakeCelery()
