from sqlalchemy.orm import Session

from app.repositories.job_repo import JobRepository
from app.schemas.job import JobCreate


def create_job(
    db: Session,
    job_data: JobCreate,
):
    return JobRepository.create_job(db, job_data)