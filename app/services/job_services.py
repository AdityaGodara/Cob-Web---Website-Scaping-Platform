from sqlalchemy.orm import Session

from app.repositories.job_repo import JobRepository
from app.schemas.job import JobCreate
from app.models.job import Job


def create_job(db: Session, job_data: JobCreate) -> Job:

    job = JobRepository.create_job(db)

    return job