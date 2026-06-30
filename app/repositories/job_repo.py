from sqlalchemy.orm import Session
from app.models.job import Job

class JobRepository:

    @staticmethod
    def create_job(db: Session) -> Job:
        job = Job()

        db.add(job)
        db.commit()
        db.refresh(job)

        return job