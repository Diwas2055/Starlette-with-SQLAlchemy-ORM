from http import HTTPStatus
from typing import List, Type

from starlette.responses import JSONResponse

from responses import ApiResponseBase, ListResponseModel, RestApiResultResponse


async def response_builder(data: dict):
    json_response = RestApiResultResponse.model_validate(data)  # Validate the data
    return JSONResponse(
        content=json_response.model_dump(exclude={"status_code"}, by_alias=True),
        status_code=int(json_response.status_code),
    )


async def convert_to_json_response(
    query: List[dict] | dict | None,
    response_model: Type[ApiResponseBase],
    messages: str,
    status_code: HTTPStatus,
):
    if isinstance(query, list) and query:
        # Validate and convert each record to the response model
        data = [response_model(**record) for record in query]
        # Create the ListResponseModel instance
        response_data = ListResponseModel[response_model](data=data)
        data = response_data.model_dump()["data"]
    elif query:
        # Validate and convert the record to the response model
        data = response_model(**query).model_dump()
    else:
        data = None
    json_data = {
        "status_code": status_code,
        "message": messages,
        "data": data,
    }
    return json_data


async def build_json_response(
    response_model: Type[ApiResponseBase],
    messages: str,
    status_code: HTTPStatus,
    query: List[dict] | dict = None,
) -> JSONResponse:
    json_data = await convert_to_json_response(
        query=query,
        response_model=response_model,
        messages=messages,
        status_code=status_code,
    )
    result = await response_builder(json_data)
    return result
