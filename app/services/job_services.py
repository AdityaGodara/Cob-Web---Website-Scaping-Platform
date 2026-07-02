from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.job import Job
from app.repositories.job_repo import JobRepository
from app.schemas.job import JobCreate
from app.workers.tasks import process_job

from app.repositories.scrape_result_repo import ScrapeResultRepository


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

def get_job(
    db,
    job_id: int,
):
    job = JobRepository.get_job_with_urls(
        db,
        job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job

def get_all_jobs(db):
    jobs = JobRepository.get_all_jobs(db)
    return jobs

def get_job_result(db, job_url_id: int):
    result = JobRepository.get_job_result(db, job_url_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Job URL not found",
        )
    return result

class ScrapeResultService:

    @staticmethod
    def get_result(
        db: Session,
        job_url_id: int,
    ):

        result = ScrapeResultRepository.get_by_job_url_id(
            db,
            job_url_id,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Scrape result not found",
            )

        return result