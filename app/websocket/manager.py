import asyncio
from collections import defaultdict
from typing import Any, DefaultDict

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.repositories.job_repo import JobRepository
from app.schemas.job import JobResponse


class ConnectionManager:
    """Tracks active WebSocket connections grouped by job ID."""

    def __init__(self) -> None:
        self.connections: DefaultDict[int, list[Any]] = defaultdict(list)

    async def connect(self, job_id: int, websocket: Any) -> None:
        self.connections[job_id].append(websocket)

    async def disconnect(self, job_id: int, websocket: Any) -> None:
        sockets = self.connections.get(job_id, [])
        if websocket in sockets:
            sockets.remove(websocket)
        if not sockets:
            self.connections.pop(job_id, None)

    async def broadcast(self, job_id: int, message: Any) -> None:
        sockets = list(self.connections.get(job_id, []))
        for websocket in sockets:
            try:
                await websocket.send_json(message)
            except Exception:
                continue


connection_manager = ConnectionManager()


def broadcast_job_update_sync(job_id: int, db: Session) -> None:
    """Serialize the latest job snapshot and push it to every connected socket."""

    job = JobRepository.get_job_with_urls(db, job_id)
    if job is None:
        return

    payload = JobResponse.model_validate(job).model_dump(mode="json")
    payload = jsonable_encoder(payload)

    try:
        asyncio.run(connection_manager.broadcast(job_id, payload))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(connection_manager.broadcast(job_id, payload))
        finally:
            loop.close()
