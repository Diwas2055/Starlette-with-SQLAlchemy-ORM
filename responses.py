from typing import Any, Generic, List, TypeVar
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic.alias_generators import to_camel


class ApiResponseBase(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        use_enum_values=True,
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


# Define a type variable
T = TypeVar("T", bound=ApiResponseBase)


class ListResponseModel(ApiResponseBase, Generic[T]):  # Inherit BaseModel first
    data: List[T]


# Pydantic model for the user
class UserResponseModel(ApiResponseBase):
    id: int
    name: str
    email: str
    is_active: bool | None = Field(default=True)

    @field_validator("name", mode="after")
    def convert_name_to_title(cls, v):
        return v.title()


class RestApiResponse(BaseModel):
    status_code: int


class RestApiResultResponse(RestApiResponse):
    message: str
    data: Any
