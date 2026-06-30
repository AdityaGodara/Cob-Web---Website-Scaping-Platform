from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine

app = FastAPI(
    title="Cob Web",
    version="v1",
    description="These APIs manage the transaction of application : CobWeb"
)

@app.get("/")
def home():
    return {"message": "Healthy", "settings": settings.app_name}