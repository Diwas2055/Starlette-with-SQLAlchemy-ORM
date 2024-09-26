from http import HTTPStatus
from starlette.requests import Request
from dependencies import get_db
from repositories import (
    bulk_create_user_repo,
    create_user_repo,
    delete_user_repo,
    get_user_repo,
    update_user_repo,
    list_user_repo,
)
from models import BulkCreateUserModel, UserCreateModel, UserUpdateModel
from starlette.routing import Route

from responses import UserResponseModel
from utils import build_json_response


# List User
async def list_user_endpoint(request: Request):
    db = request.state.db
    users = await list_user_repo(db)
    return await build_json_response(
        query=users,
        response_model=UserResponseModel,
        messages="Users retrieved successfully.",
        status_code=HTTPStatus.OK,
    )


# Create User
async def create_user_endpoint(request: Request):
    db = get_db(request)
    data = await request.json()
    user_data = UserCreateModel.model_validate(data)
    users = await create_user_repo(user_data.model_dump(), db)
    return await build_json_response(
        query=users,
        response_model=UserResponseModel,
        status_code=HTTPStatus.CREATED,
        messages="User created successfully.",
    )


# Read User
async def get_user_endpoint(request: Request):
    db = get_db(request)
    user_id = int(request.path_params["user_id"])
    user = await get_user_repo(user_id, db=db)
    return await build_json_response(
        query=user,
        response_model=UserResponseModel,
        messages="User retrieved successfully.",
        status_code=HTTPStatus.OK,
    )


# Update User
async def update_user_endpoint(request: Request):
    db = get_db(request)
    user_id = int(request.path_params["user_id"])
    data = await request.json()
    update_data = UserUpdateModel(**data).dict(exclude_unset=True)

    updated_user = await update_user_repo(user_id, update_data, db)
    return await build_json_response(
        query=updated_user,
        response_model=UserResponseModel,
        messages="User updated successfully.",
        status_code=HTTPStatus.OK,
    )


# Delete User
async def delete_user_endpoint(request: Request):
    db = get_db(request)
    user_id = int(request.path_params["user_id"])
    await delete_user_repo(user_id, db)
    return await build_json_response(
        response_model=UserResponseModel,
        messages="User deleted successfully.",
        status_code=HTTPStatus.OK,
    )


# Bulk Create User
async def bulk_create_user_endpoint(request: Request):
    db = get_db(request)
    data = await request.json()
    bulk_create_model = BulkCreateUserModel.model_validate(data)
    create_users = await bulk_create_user_repo(bulk_create_model.model_dump(), db)
    return await build_json_response(
        query=create_users,
        response_model=UserResponseModel,
        messages="Bulk user created successfully.",
        status_code=HTTPStatus.CREATED,
    )


routes = [
    Route("/", endpoint=list_user_endpoint, methods=["GET"]),
    Route("/", endpoint=create_user_endpoint, methods=["POST"]),
    Route("/bulk/", endpoint=bulk_create_user_endpoint, methods=["POST"]),
    Route("/{user_id:int}/", endpoint=get_user_endpoint, methods=["GET"]),
    Route("/{user_id:int}/", endpoint=update_user_endpoint, methods=["PATCH"]),
    Route("/{user_id:int}/", endpoint=delete_user_endpoint, methods=["DELETE"]),
]
