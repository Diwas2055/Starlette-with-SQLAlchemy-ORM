# Pydantic Models for request validation
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class UserCreateModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        alias_generator=to_camel,
    )
    name: str
    email: str
    is_active: bool = Field(default=True)


class UserUpdateModel(BaseModel):
    name: str = None
    email: str = None
    is_active: bool = None


class BulkCreateUserModel(BaseModel):
    users: List[UserCreateModel]
