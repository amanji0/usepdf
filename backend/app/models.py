"""Pydantic request / response models."""

from pydantic import BaseModel, field_validator


class JobResponse(BaseModel):
    """Returned immediately when a task is enqueued."""

    job_id: str
    status: str = "queued"


class JobStatus(BaseModel):
    """Full status payload for a running or completed job."""

    job_id: str
    status: str
    progress: int | None = None
    download_url: str | None = None
    error: str | None = None
    filename: str | None = None


class SplitOptions(BaseModel):
    """Page-range specification for the split tool."""

    ranges: str  # e.g. "1-3,5,7-9" or "all"


class RotateOptions(BaseModel):
    """Rotation parameters."""

    angle: int
    pages: str | None = None  # comma-separated page numbers, e.g. "1,3,5"

    @field_validator("angle")
    @classmethod
    def validate_angle(cls, v: int) -> int:
        if v not in (90, 180, 270):
            raise ValueError("angle must be 90, 180, or 270")
        return v


class CompressOptions(BaseModel):
    """Compression level selector."""

    level: str = "recommended"

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        allowed = {"low", "recommended", "extreme"}
        if v not in allowed:
            raise ValueError(f"level must be one of {allowed}")
        return v


class ProtectOptions(BaseModel):
    """Password-protect request."""

    password: str


class UnlockOptions(BaseModel):
    """Unlock (decrypt) request."""

    password: str
