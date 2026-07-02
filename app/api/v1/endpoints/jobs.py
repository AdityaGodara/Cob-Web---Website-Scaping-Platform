from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse
from app.services.job_services import create_job as serv_job, get_job as serv_get_job, get_all_jobs as serv_get_all_jobs
from app.schemas.job import ScrapeResultResponse
from app.services.job_services import ScrapeResultService

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)

@router.post("/", response_model=JobResponse, status_code=201)
def create_job( job: JobCreate, db: Session = Depends(get_db) ):
    created_job = serv_job(db,job)

    return created_job

@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    # print(f"Fetching job with ID: {job_id}")
    job = serv_get_job(db, job_id)

    return job

@router.get("/")
def list_jobs(db: Session = Depends(get_db)):
    return serv_get_all_jobs(db)

@router.get("/job_urls/{job_url_id}/result")
def get_job_result(job_url_id: int, db: Session = Depends(get_db)):
    
    return ScrapeResultService.get_result(db, job_url_id)