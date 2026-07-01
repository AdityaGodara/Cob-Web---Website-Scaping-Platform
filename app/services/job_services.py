from sqlalchemy.orm import Session

from app.repositories.job_repo import JobRepository
from app.schemas.job import JobCreate
from app.workers.tasks import process_job


def create_job(
    db: Session,
    job_data: JobCreate,
):
    job = JobRepository.create_job(
        db,
        job_data,
    )

    process_job.delay(job.id)

    return job