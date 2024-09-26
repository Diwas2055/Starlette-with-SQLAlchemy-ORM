# CRUD operations with advanced transaction handling, including exception management.
from http import HTTPStatus
import databases
from sqlalchemy import desc, func, insert, update
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException

from schemas import User


# List Users
async def list_user_repo(db: databases.Database):
    query = User.__table__.select().order_by(func.lower(User.name).asc())
    users = await db.fetch_all(query)
    return users


# Create User with Transaction Management
async def create_user_repo(data, db: databases.Database):
    query = (
        insert(User)
        .values(**data)
        .returning(
            User.id,
            User.name,
            User.email,
            User.is_active,
        )
    )  # Select columns you want to return

    try:
        user = await db.fetch_one(query)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )
    else:
        return user


# Read User
async def get_user_repo(user_id: int, db: databases.Database):
    query = User.__table__.select().where(User.id == user_id)
    user = await db.fetch_one(query)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


# Update User with Transactions and Exception Handling
async def update_user_repo(user_id: int, update_data: dict, db: databases.Database):
    await get_user_repo(user_id, db)
    query = (
        update(User)
        .where(User.id == user_id)
        .values(**update_data)
        .returning(
            User.id,
            User.name,
            User.email,
            User.is_active,
        )
    )  # Select columns you want to return
    await db.execute(query)

    # Ensure changes are committed before returning user
    updated_user = await get_user_repo(user_id, db)
    return updated_user


# Delete User (with cascading delete of addresses)
async def delete_user_repo(user_id: int, db: databases.Database):
    await get_user_repo(user_id, db)
    query = User.__table__.delete().where(User.id == user_id)
    await db.execute(query)
    return {"message": "User deleted"}


# Bulk Create Users with Transactions and Exception Handling


async def bulk_create_user_repo(data, db: databases.Database):
    bulk_data = data["users"]

    # Prepare the insert query with RETURNING clause to return the inserted data
    query = (
        insert(User)
        .values(bulk_data)
        .returning(
            User.id,
            User.name,
            User.email,
            User.is_active,
        )  # Select columns you want to return
    )

    try:
        # Fetch the inserted records (including auto-generated ids)
        inserted_users = await db.fetch_all(query)
    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="One or more users already exist"
        )
    else:
        # Return the list of inserted users
        return inserted_users
