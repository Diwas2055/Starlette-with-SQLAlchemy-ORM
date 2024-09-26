from logger_setup import logger
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocketDisconnect

from ws_connection import (
    connection_manager,
    handle_websocket_message,
)


# WebSocket endpoint function
async def websocket_endpoint(websocket):
    connection_id = await connection_manager.connect(websocket)

    try:
        while True:
            try:
                data = await websocket.receive_text()
                await handle_websocket_message(connection_id, data)

            except WebSocketDisconnect:
                logger.info(f"Client {connection_id} disconnected.")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket {connection_id}: {e}")
                await connection_manager.send_message(
                    connection_id, {"type": "error", "message": "An error occurred."}
                )
    finally:
        await connection_manager.disconnect(connection_id)


async def broadcast_message(request):
    message = {"type": "broadcast", "message": "This is a broadcast message"}
    await connection_manager.broadcast(message)
    return JSONResponse({"detail": "Message broadcasted"})


routes = [
    WebSocketRoute(path="/ws/", endpoint=websocket_endpoint),
    Route("/broadcast/", broadcast_message, methods=["Get"]),
]
