from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine

from app.api.v1.router import api_router
from app.websocket.routes import router as websocket_router

app = FastAPI(
    title="Cob Web",
    version="v1",
    description="These APIs manage the transaction of application : CobWeb"
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router)

@app.get("/")
def home():
    return {"message": "Healthy", "settings": settings.redis_url}