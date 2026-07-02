from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.job import JobResponse
from app.services.job_services import get_job as serv_get_job
from app.websocket.manager import connection_manager

router = APIRouter(prefix="/ws/jobs", tags=["websocket"])


@router.websocket("/{job_id}")
async def job_updates(websocket: WebSocket, job_id: int, db: Session = Depends(get_db)) -> None:
    await websocket.accept()

    await connection_manager.connect(job_id, websocket)

    try:
        job = serv_get_job(db, job_id)
        payload = JobResponse.model_validate(job).model_dump(mode="json")
        await websocket.send_json(jsonable_encoder(payload))

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await connection_manager.disconnect(job_id, websocket)
    except Exception:
        await connection_manager.disconnect(job_id, websocket)
        raise
