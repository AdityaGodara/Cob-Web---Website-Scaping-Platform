from app.db.database import SessionLocal
from app.models.job import JobStatus
from app.models.job_url import JobURLStatus
from app.repositories.job_repo import JobRepository
from app.repositories.joburl_repo import JobURLRepository
from app.repositories.scrape_result_repo import ScrapeResultRepository
from app.scrapper.scraper import scrape
from app.workers.celery_app import celery_app


class RetryableScraperError(Exception):
    pass


class NonRetryableScraperError(Exception):
    pass

@celery_app.task(rate_limit="10/m", bind=True, max_retries=3, default_retry_delay=30)
def process_job(self, job_id: int):

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

        total_urls = len(urls)
        completed_urls = 0

        for job_url in urls:
            try:
                JobURLRepository.update_status(
                    db,
                    job_url,
                    JobURLStatus.RUNNING,
                )

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

                completed_urls += 1
                progress = int((completed_urls / total_urls) * 100)
                JobRepository.update_job_progress(
                    db=db,
                    job=job,
                    progress=progress,
                )
            except Exception as e:
                print(e)

                JobURLRepository.update_status(
                    db,
                    job_url,
                    JobURLStatus.FAILED,
                )
                continue

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