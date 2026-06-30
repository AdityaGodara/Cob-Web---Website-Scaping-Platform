from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine

from app.api.v1.router import api_router

app = FastAPI(
    title="Cob Web",
    version="v1",
    description="These APIs manage the transaction of application : CobWeb"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "Healthy", "settings": settings.app_name}