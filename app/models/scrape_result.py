from app.models.base import Base

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

class ScrapeResult(Base):
    __tablename__ = "scrape_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_url_id: Mapped[int] = mapped_column(ForeignKey("job_urls.id"), nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    job_url: Mapped["JobURL"] = relationship(back_populates="scrape_result")