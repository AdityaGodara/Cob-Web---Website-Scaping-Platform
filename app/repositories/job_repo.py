from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_url import JobURL
from app.schemas.job import JobCreate


class JobRepository:

    @staticmethod
    def create_job(
        db: Session,
        job_data: JobCreate,
    ) -> Job:

        job = Job()

        db.add(job)

        db.flush()

        job_urls = [
            JobURL(
                job_id=job.id,
                url=str(url),
            )
            for url in job_data.urls
        ]

        db.add_all(job_urls)

        db.commit()

        db.refresh(job)

        return job