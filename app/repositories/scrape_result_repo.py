from sqlalchemy.orm import Session

from app.models.scrape_result import ScrapeResult


class ScrapeResultRepository:

    @staticmethod
    def create(
        db: Session,
        job_url_id: int,
        data: dict,
    ) -> ScrapeResult:

        result = ScrapeResult(
            job_url_id=job_url_id,
            data=data,
        )

        db.add(result)
        db.commit()
        db.refresh(result)

        return result