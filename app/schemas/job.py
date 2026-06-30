from pydantic import BaseModel, HttpUrl, Field

from app.models.job import JobStatus

class JobCreate(BaseModel):
    urls: list[HttpUrl] = Field(..., min_length=1)

class JobResponse(BaseModel):
    id: int
    status: JobStatus

    model_config = {
        "from_attributes": True
    }