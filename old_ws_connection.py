from logger_setup import logger
from asyncio import TaskGroup, gather, get_event_loop, sleep, ensure_future


HEARTBEAT_INTERVAL = 30  # seconds
HEARTBEAT_TIMEOUT = 10  # seconds


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
        self.cleanup_task = ensure_future(self._cleanup_inactive_connections())

    async def connect(self, websocket):
        """Accept the WebSocket connection and add it to active connections."""
        try:
            await websocket.accept()  # Ensure that accept is called before interacting
            self.active_connections = {
                **self.active_connections,
                websocket: {
                    "last_pong": get_event_loop().time(),
                    "pong_received": True,
                },
            }
            logger.info(
                f"New WebSocket connection. Total connections: {len(self.active_connections)}"
            )
        except Exception as e:
            logger.error(f"Error during WebSocket accept: {e}")
            await self.disconnect(websocket)

    async def disconnect(self, websocket):
        """Safely disconnect the WebSocket."""
        if websocket in self.active_connections:
            del self.active_connections[websocket]
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error while closing WebSocket: {e}")
            logger.info(
                f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
            )

    async def send_message(self, websocket, message):
        """Send a JSON message to the WebSocket if it's in active connections."""
        if websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                await self.disconnect(websocket)

    async def broadcast(self, message):
        """Broadcast a message to all active WebSocket connections."""
        websockets_to_remove = await gather(
            *[self._safe_send(ws, message) for ws in self.active_connections]
        )
        await gather(*[self.disconnect(ws) for ws in websockets_to_remove if ws])

    async def pong_received(self, websocket):
        """Update pong received timestamp."""
        if websocket in self.active_connections:
            self.active_connections[websocket] = {
                **self.active_connections[websocket],
                "last_pong": get_event_loop().time(),
                "pong_received": True,
            }
            logger.info("Pong received from client.")

    async def send_heartbeat(self):
        """Send periodic pings to check if WebSockets are still active."""
        websockets_to_remove = await gather(
            *[self._send_ping(ws, data) for ws, data in self.active_connections.items()]
        )
        await gather(*[self.disconnect(ws) for ws in websockets_to_remove if ws])

    async def _send_ping(self, websocket, data):
        """Send a ping message to the WebSocket and handle pong response."""
        if not data["pong_received"]:
            return websocket  # WebSocket didn't respond, mark for removal
        try:
            await websocket.send_text("ping")
            logger.info(f"Ping sent to client {websocket}.")
            self.active_connections[websocket] = {
                **data,
                "pong_received": False,
            }
        except Exception as e:
            logger.error(f"Error sending ping: {e}")
            return websocket

    async def _safe_send(self, websocket, message):
        """Safely send a message to the WebSocket, catching errors."""
        try:
            await websocket.send_json(message)
        except Exception:
            return websocket

    async def _cleanup_inactive_connections(self):
        """Periodically remove inactive WebSockets."""
        while True:
            current_time = get_event_loop().time()
            websockets_to_remove = [
                ws
                for ws, data in self.active_connections.items()
                if current_time - data["last_pong"] > HEARTBEAT_TIMEOUT
            ]
            await gather(*[self.disconnect(ws) for ws in websockets_to_remove])
            await sleep(HEARTBEAT_INTERVAL)


connection_manager = ConnectionManager()


# Heartbeat scheduling with Python 3.11 TaskGroup for better management
async def periodic_heartbeat():
    async with TaskGroup() as tg:
        tg.create_task(connection_manager.send_heartbeat())
        await sleep(HEARTBEAT_INTERVAL)


# Handle WebSocket messages
async def handle_websocket_message(websocket, data):
    match data:
        case "pong":
            await connection_manager.pong_received(websocket)
        case _:
            logger.info(f"Message received: {data}")
            await connection_manager.send_message(
                websocket, {"type": "response", "message": "Message received"}
            )
