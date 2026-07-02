from sqlalchemy.orm import Session, joinedload

from app.models.job import Job, JobStatus
from app.models.job_url import JobURL
from app.schemas.job import JobCreate


class JobRepository:

    @staticmethod
    def create_job(db: Session, job_data: JobCreate) -> Job:
        job = Job()

        db.add(job)
        db.flush()

        urls = [
            JobURL(
                job_id=job.id,
                url=str(url),
            )
            for url in job_data.urls
        ]

        db.add_all(urls)

        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def get_job(db: Session, job_id: int):
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def update_job_status(
        db: Session,
        job_id: int,
        status: JobStatus,
    ):
        job = JobRepository.get_job(db, job_id=job_id)
        if job:
            job.status = status

    @staticmethod
    def update_job_progress(
        db: Session,
        job_id: int,
        progress: int,
    ):
        job = JobRepository.get_job(db, job_id=job_id)
        if job:
            job.progress = progress

        # db.commit()
        # db.refresh(job)

    @staticmethod
    def get_job_with_urls(db: Session, job_id: int):
        return (
            db.query(Job)
            .filter(Job.id == job_id)
            .options(
                joinedload(Job.urls)
            )
            .filter(Job.id == job_id)
            .first()
        )
    
    @staticmethod
    def get_all_jobs(db: Session):
        return db.query(Job).all()