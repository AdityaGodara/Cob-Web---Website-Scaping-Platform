from urllib.parse import urlparse

from app.db.database import SessionLocal
from app.models.job import JobStatus
from app.models.job_url import JobURL, JobURLStatus
from app.repositories.job_repo import JobRepository
from app.repositories.joburl_repo import JobURLRepository
from app.repositories.scrape_result_repo import ScrapeResultRepository
from app.scrapper.scraper import scrape, ScraperError
from app.workers.celery_app import celery_app
from app.websocket.manager import broadcast_job_update_sync

from celery import group, chord

class RetryableScraperError(Exception):
    pass


class NonRetryableScraperError(Exception):
    pass


def build_failure_result_data(message: str, error_type: str = "server_error") -> dict:
    return {
        "status": "failed",
        "error": True,
        "error_type": error_type,
        "message": message,
    }


@celery_app.task(rate_limit="10/m", bind=True, max_retries=3, default_retry_delay=30)
def process_job(self, job_id: int):
    db = SessionLocal()

    try:
        job = JobRepository.get_job(db, job_id)

        JobRepository.update_job_status(
            db,
            job_id,
            JobStatus.RUNNING,
        )

        db.commit()
        broadcast_job_update_sync(job_id, db)

        urls = JobURLRepository.get_urls(db, job_id)

        tasks = [
            scrape_url.s(job_url.id)
            for job_url in urls
        ]

        chord(group(tasks))(
            finalize_job.s(job_id)
        )

    finally:
        db.close()


@celery_app.task(
    bind=True,
    autoretry_for=(RetryableScraperError,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=5,
)
def scrape_url(self, job_url_id: int):

    db = SessionLocal()

    try:

        job_url = JobURLRepository.get_by_id(
            db,
            job_url_id,
        )

        if job_url is None:
            return False

        JobURLRepository.update_status(
            db,
            job_url,
            JobURLStatus.RUNNING,
        )

        parsed = urlparse(job_url.url)
        is_valid_url = bool(parsed.scheme in {"http", "https"} and parsed.netloc)
        if not is_valid_url:
            message = "Invalid URL format"
            ScrapeResultRepository.create(
                db=db,
                job_url_id=job_url.id,
                data=build_failure_result_data(message, error_type="invalid_url"),
            )
            JobURLRepository.update_status(
                db,
                job_url,
                JobURLStatus.FAILED,
            )
            JobURLRepository.update_error_message(db, job_url, message)
            db.commit()
            broadcast_job_update_sync(job_url.job_id, db)
            return False

        result = scrape(job_url.url)

        ScrapeResultRepository.create(
            db=db,
            job_url_id=job_url.id,
            data=result,
        )

        JobURLRepository.update_status(
            db,
            job_url,
            JobURLStatus.SUCCESS,
        )
        JobURLRepository.update_error_message(db, job_url, None)

        completed = JobURLRepository.count_completed_urls(db, job_url.job_id)
        total = JobURLRepository.count_urls(db, job_url.job_id)
        if total > 0:
            progress = int((completed / total) * 100)
            JobRepository.update_job_progress(db, job_url.job_id, progress)

        db.commit()
        broadcast_job_update_sync(job_url.job_id, db)
        return True

    except ScraperError as exc:

        db.rollback()

        if job_url is not None:
            JobURLRepository.update_status(
                db,
                job_url,
                JobURLStatus.FAILED,
            )
            JobURLRepository.update_error_message(db, job_url, str(exc))
            ScrapeResultRepository.create(
                db=db,
                job_url_id=job_url.id,
                data=build_failure_result_data(str(exc), error_type="server_error"),
            )

            completed = JobURLRepository.count_completed_urls(db, job_url.job_id)
            total = JobURLRepository.count_urls(db, job_url.job_id)
            if total > 0:
                progress = int((completed / total) * 100)
                JobRepository.update_job_progress(db, job_url.job_id, progress)

            db.commit()
            broadcast_job_update_sync(job_url.job_id, db)

        return False

    except NonRetryableScraperError as exc:

        db.rollback()

        if job_url is not None:
            JobURLRepository.update_status(
                db,
                job_url,
                JobURLStatus.FAILED,
            )
            JobURLRepository.update_error_message(db, job_url, str(exc))
            ScrapeResultRepository.create(
                db=db,
                job_url_id=job_url.id,
                data=build_failure_result_data(str(exc), error_type="server_error"),
            )

            completed = JobURLRepository.count_completed_urls(db, job_url.job_id)
            total = JobURLRepository.count_urls(db, job_url.job_id)
            if total > 0:
                progress = int((completed / total) * 100)
                JobRepository.update_job_progress(db, job_url.job_id, progress)

            db.commit()
            broadcast_job_update_sync(job_url.job_id, db)

        return False

    except Exception as exc:

        db.rollback()

        if job_url is not None:
            JobURLRepository.update_status(
                db,
                job_url,
                JobURLStatus.FAILED,
            )
            JobURLRepository.update_error_message(db, job_url, f"Unexpected server error: {exc}")
            ScrapeResultRepository.create(
                db=db,
                job_url_id=job_url.id,
                data=build_failure_result_data(f"Unexpected server error: {exc}", error_type="server_error"),
            )

            completed = JobURLRepository.count_completed_urls(db, job_url.job_id)
            total = JobURLRepository.count_urls(db, job_url.job_id)
            if total > 0:
                progress = int((completed / total) * 100)
                JobRepository.update_job_progress(db, job_url.job_id, progress)

            db.commit()
            broadcast_job_update_sync(job_url.job_id, db)

        return False

    finally:

        db.close()

@celery_app.task
def finalize_job(results, job_id: int):
    db = SessionLocal()

    total = len(results)
    progress = 100 if total > 0 else 0

    JobRepository.update_job_progress(db, job_id, progress)

    if all(results):
        JobRepository.update_job_status(db, job_id, JobStatus.SUCCESS)
    else:
        JobRepository.update_job_status(db, job_id, JobStatus.FAILED)

    db.commit()
    broadcast_job_update_sync(job_id, db)
    db.close()