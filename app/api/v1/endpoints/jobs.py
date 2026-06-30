from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services.job_services import create_job as serv_job

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)

@router.post("/", response_model=JobResponse, status_code=201)
def create_job( job: JobCreate, db: Session = Depends(get_db) ):
    created_job = serv_job(db,job)

    return created_job