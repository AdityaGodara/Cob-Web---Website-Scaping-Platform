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
    def get_by_id(db: Session, job_url_id: int):
        return (
            db.query(JobURL)
            .filter(JobURL.id == job_url_id)
            .first()
        )
    
    @staticmethod
    def count_urls(db: Session, job_id: int):
        return (
            db.query(JobURL)
            .filter(JobURL.job_id == job_id)
            .count()
        )
    
    @staticmethod
    def count_completed_urls(db: Session, job_id: int):
        return (
            db.query(JobURL)
            .filter(
                JobURL.job_id == job_id,
                JobURL.status.in_([JobURLStatus.SUCCESS, JobURLStatus.FAILED]),
            )
            .count()
        )

    @staticmethod
    def update_status(
        db: Session,
        job_url: JobURL,
        status: JobURLStatus,
    ):
        job_url.status = status

        # db.commit()
        # db.refresh(job_url)

    @staticmethod
    def get_result(db: Session, job_url_id: int):
        return (
            db.query(JobURL)
            .filter(JobURL.id == job_url_id)
            .first()
        )