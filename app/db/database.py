print("databse.py loaded ")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.config import settings

engine = create_engine(
    settings.db_url,
    echo=settings.debug
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.scalar())