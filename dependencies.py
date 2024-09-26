from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession


def get_config(request: Request):
    return request.app.state.config


def get_db(request: Request) -> AsyncSession:
    return request.state.db
