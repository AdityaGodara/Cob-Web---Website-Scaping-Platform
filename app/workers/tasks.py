from app.db.database import SessionLocal
from app.models.job import JobStatus
from app.models.job_url import JobURLStatus
from app.repositories.job_repo import JobRepository
from app.repositories.joburl_repo import JobURLRepository
from app.scrapper.scraper import scrape
from app.workers.celery_app import celery_app


@celery_app.task
def process_job(job_id: int):

    db = SessionLocal()

    try:
        job = JobRepository.get_job(db, job_id)

        if job is None:
            print(f"Job {job_id} not found")
            return

        JobRepository.update_job_status(
            db,
            job,
            JobStatus.RUNNING,
        )

        urls = JobURLRepository.get_urls(
            db,
            job_id,
        )

        for job_url in urls:

            JobURLRepository.update_status(
                db,
                job_url,
                JobURLStatus.RUNNING,
            )

            result = scrape(job_url.url)

            print(result)

            JobURLRepository.update_status(
                db,
                job_url,
                JobURLStatus.SUCCESS,
            )

        JobRepository.update_job_status(
            db,
            job,
            JobStatus.SUCCESS,
        )

    except Exception as e:

        print(e)

        JobRepository.update_job_status(
            db,
            job,
            JobStatus.FAILED,
        )

    finally:
        db.close()