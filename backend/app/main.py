"""FastAPI application entry point for UsePDF."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.routes import tools, jobs, downloads

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.RESULT_DIR).mkdir(parents=True, exist_ok=True)
    logger.info("UsePDF API starting up — storage directories ready.")
    yield
    logger.info("UsePDF API shutting down.")


app = FastAPI(
    title="UsePDF API",
    description="Self-hosted PDF toolkit API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


app.include_router(tools.router)
app.include_router(jobs.router)
app.include_router(downloads.router)
