from sqlalchemy.orm import Session

from app.models.scrape_result import ScrapeResult

from app.models.scrape_result import ScrapeResult


class ScrapeResultRepository:

    @staticmethod
    def create(
        db: Session,
        job_url_id: int,
        data: dict,
    ):
        scrape_result = ScrapeResult(
            job_url_id=job_url_id,
            data=data,
        )

        db.add(scrape_result)

        return scrape_result

    @staticmethod
    def get_by_job_url_id(
        db: Session,
        job_url_id: int,
    ):
        return (
            db.query(ScrapeResult)
            .filter(
                ScrapeResult.job_url_id == job_url_id
            )
            .first()
        )