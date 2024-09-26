import asyncio
import uuid  # For generating unique connection IDs

from logger_setup import logger

HEARTBEAT_INTERVAL = 30  # seconds
HEARTBEAT_TIMEOUT = 10  # seconds


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  # Stores connection data by ID
        self.cleanup_task = asyncio.create_task(self._cleanup_inactive_connections())

    async def connect(self, websocket):
        """Accept the WebSocket connection, assign a unique ID, and add to active connections."""
        try:
            await websocket.accept()
            connection_id = str(uuid.uuid4())  # Generate a unique ID for the connection
            self.active_connections[connection_id] = {
                "websocket": websocket,
                "last_pong": asyncio.get_event_loop().time(),
                "pong_received": True,
            }
            logger.info(
                f"New WebSocket connection with ID {connection_id}. "
                f"Total connections: {len(self.active_connections)}"
            )
            await websocket.send_json(
                {"type": "connection_id", "id": connection_id}
            )  # Optionally send the ID to the client
            return connection_id
        except Exception as e:
            logger.error(f"Error during WebSocket accept: {e}")
            await self.disconnect_by_websocket(websocket)

    async def disconnect(self, connection_id):
        """Safely disconnect the WebSocket using its connection ID."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]["websocket"]
            del self.active_connections[connection_id]
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error while closing WebSocket {connection_id}: {e}")
            logger.info(
                f"WebSocket {connection_id} disconnected. "
                f"Total connections: {len(self.active_connections)}"
            )

    async def disconnect_by_websocket(self, websocket):
        """Disconnect by WebSocket object if connection ID is unknown."""
        connection_id = self.get_connection_id_by_websocket(websocket)
        if connection_id:
            await self.disconnect(connection_id)

    def get_connection_id_by_websocket(self, websocket):
        """Find the connection ID by the WebSocket object."""
        for connection_id, data in self.active_connections.items():
            if data["websocket"] == websocket:
                return connection_id
        return None

    async def send_message(self, connection_id, message):
        """Send a JSON message to the WebSocket identified by connection ID."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]["websocket"]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket {connection_id}: {e}")
                await self.disconnect(connection_id)

    async def broadcast(self, message):
        """Broadcast a message to all active WebSocket connections."""
        websockets_to_remove = await asyncio.gather(
            *[
                self._safe_send(connection_id, message)
                for connection_id in self.active_connections
            ]
        )
        await asyncio.gather(
            *[self.disconnect(conn_id) for conn_id in websockets_to_remove if conn_id]
        )

    async def pong_received(self, connection_id):
        """Update pong received timestamp for the given connection ID."""
        if connection_id in self.active_connections:
            self.active_connections[connection_id]["last_pong"] = (
                asyncio.get_event_loop().time()
            )
            self.active_connections[connection_id]["pong_received"] = True
            logger.info(f"Pong received from client {connection_id}.")

    async def send_heartbeat(self):
        """Send periodic pings to check if WebSockets are still active."""
        websockets_to_remove = await asyncio.gather(
            *[
                self._send_ping(connection_id, data)
                for connection_id, data in self.active_connections.items()
            ]
        )
        await asyncio.gather(
            *[self.disconnect(conn_id) for conn_id in websockets_to_remove if conn_id]
        )

    async def _send_ping(self, connection_id, data):
        """Send a ping message to the WebSocket and handle pong response."""
        websocket = data["websocket"]
        if not data["pong_received"]:
            return connection_id  # WebSocket didn't respond, mark for removal
        try:
            await websocket.send_text("ping")
            logger.info(f"Ping sent to client {connection_id}.")
            self.active_connections[connection_id]["pong_received"] = False
        except Exception as e:
            logger.error(f"Error sending ping to WebSocket {connection_id}: {e}")
            return connection_id

    async def _safe_send(self, connection_id, message):
        """Safely send a message to the WebSocket, catching errors."""
        websocket = self.active_connections[connection_id]["websocket"]
        try:
            await websocket.send_json(message)
        except Exception:
            return connection_id

    async def _cleanup_inactive_connections(self):
        """Periodically remove inactive WebSockets."""
        while True:
            current_time = asyncio.get_event_loop().time()
            websockets_to_remove = [
                connection_id
                for connection_id, data in self.active_connections.items()
                if current_time - data["last_pong"] > HEARTBEAT_TIMEOUT
            ]
            await asyncio.gather(
                *[self.disconnect(conn_id) for conn_id in websockets_to_remove]
            )
            await asyncio.sleep(HEARTBEAT_INTERVAL)


connection_manager = ConnectionManager()


# Handle WebSocket messages
async def handle_websocket_message(connection_id, data):
    match data:
        case "pong":
            await connection_manager.pong_received(connection_id)
        case _:
            logger.info(f"Message received from {connection_id}: {data}")
            await connection_manager.send_message(
                connection_id, {"type": "response", "message": "Message received"}
            )


# Heartbeat task
async def periodic_heartbeat():
    """Send heartbeat pings periodically to all active WebSockets."""
    async with asyncio.TaskGroup() as tg:
        tg.create_task(connection_manager.send_heartbeat())
        await asyncio.sleep(HEARTBEAT_INTERVAL)
