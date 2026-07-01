from sqlalchemy.orm import Session

from app.models.job_url import JobURL, JobURLStatus


class JobURLRepository:

    @staticmethod
    def get_urls(db: Session, job_id: int):
        return (
            db.query(JobURL)
            .filter(JobURL.job_id == job_id)
            .all()
        )

    @staticmethod
    def update_status(
        db: Session,
        job_url: JobURL,
        status: JobURLStatus,
    ):
        job_url.status = status

        db.commit()
        db.refresh(job_url)