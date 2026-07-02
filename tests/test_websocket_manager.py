import asyncio

from app.websocket.manager import ConnectionManager


class DummyWebSocket:
    def __init__(self) -> None:
        self.sent_messages: list[object] = []

    async def send_json(self, message: object) -> None:
        self.sent_messages.append(message)


def test_manager_tracks_connections_and_broadcasts_messages() -> None:
    async def run_test() -> None:
        manager = ConnectionManager()
        ws_one = DummyWebSocket()
        ws_two = DummyWebSocket()

        await manager.connect(42, ws_one)
        await manager.connect(42, ws_two)

        await manager.broadcast(42, {"status": "RUNNING", "progress": 25})

        assert ws_one.sent_messages == [{"status": "RUNNING", "progress": 25}]
        assert ws_two.sent_messages == [{"status": "RUNNING", "progress": 25}]

        await manager.disconnect(42, ws_one)
        assert len(manager.connections[42]) == 1

    asyncio.run(run_test())
