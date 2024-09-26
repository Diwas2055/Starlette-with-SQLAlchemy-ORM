from asyncio import ensure_future
import contextlib
from logger_setup import logger

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount

from config import database, engine
from middleware import DBSessionMiddleware
from routes import user
from routes.websocket import test as ws_test
from schemas import Base
from ws_connection import periodic_heartbeat


async def http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        {"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers
    )


@contextlib.asynccontextmanager
async def lifespan(app):
    await database.connect()
    logger.info("Connected to database")
    async with engine.begin() as conn:
        # Bind the models to the engine
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Created tables")

    # Add the heartbeat task on startup
    ensure_future(periodic_heartbeat())
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Dropped tables")
    await database.disconnect()
    logger.info("Disconnected from database")


def _init_routes():
    return [
        Mount("/users", routes=user.routes),
        Mount("/", routes=ws_test.routes),
    ]


exception_handlers = {HTTPException: http_exception}
app = Starlette(
    debug=True,
    middleware=[
        Middleware(DBSessionMiddleware),
    ],
    lifespan=lifespan,
    routes=_init_routes(),
    exception_handlers=exception_handlers,
)


@app.route("/")
async def homepage(request):
    return JSONResponse({"hello": "world"})


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000)
