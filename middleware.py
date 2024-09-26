from logger_setup import logger
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from config import database


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable]
    ):
        request.state.db = database
        logger.info(f"Request: {request.url}")
        response = await call_next(request)
        return response
        #! This is the middleware that will be used to manage transactions.
        #! It is not used in the final version of the project.
        #! The code is kept here for reference purposes.
        # try:
        #     async with database.transaction():
        #         logger.info(f"Transaction started for request: {request.url}")
        #         response = await call_next(request)
        #         logger.info(f"Transaction committed for request: {request.url}")
        #         return response
        # except Exception as e:
        #     logger.error(
        #         f"Transaction rolled back for request: {request.url}. Error: {str(e)}"
        #     )
        #     return JSONResponse({"error": str(e)}, status_code=500)
