from app.models.base import Base
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, func
from sqlalchemy.orm import Mapped, mapped_column

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    status: Mapped[JobStatus] = mapped_column(
        SqlEnum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )