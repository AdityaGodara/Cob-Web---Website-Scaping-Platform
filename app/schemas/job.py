from pydantic import BaseModel, HttpUrl, Field

from app.models.job import JobStatus
from app.models.job_url import JobURLStatus

class JobCreate(BaseModel):
    urls: list[HttpUrl] = Field(..., min_length=1)

class JobURLResponse(BaseModel):
    id: int
    url: str
    status: JobURLStatus

    model_config = {
        "from_attributes": True
    }

class JobResponse(BaseModel):
    id: int
    status: JobStatus
    progress: int

    urls: list[JobURLResponse]

    model_config = {
        "from_attributes": True
    }

class ScrapeResultResponse(BaseModel):
    id: int
    job_url_id: int
    data: dict

    model_config = {
        "from_attributes": True
    }