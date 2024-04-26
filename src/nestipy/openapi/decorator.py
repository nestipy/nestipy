import dataclasses
from typing import Union, Optional, Any, Type

from nestipy_metadata import SetMetadata
from openapidocs.v3 import RequestBody, Response, Parameter
from openapidocs.v3 import SecurityRequirement, MediaType, Schema
from pydantic import TypeAdapter, BaseModel


def ApiBody(body: Union[BaseModel, Type] = None, consumer: str = 'application/json'):
    content: dict = {}
    if dataclasses.is_dataclass(body):
        content: dict = TypeAdapter(body).json_schema()
    elif isinstance(body, BaseModel):
        content: dict = body.model_json_schema()
    body = RequestBody(
        content={
            consumer: MediaType(
                schema=Schema(**content)
            )
        },
        required=True
    )
    return SetMetadata(key='__openapi__request_body', data=body)


def ApiResponse(status: int, response: Response):
    return SetMetadata(key='__openapi__responses', data={status: response}, as_dict=True)


def ApiOkResponse(description: Optional[str] = None, schema: Schema = None, example: Any = None):
    return ApiResponse(
        status=200,
        response=Response(
            description or 'Success response',
            content={
                'application/json': MediaType(
                    schema=schema or Schema(),
                    example=example
                )
            }
        )
    )


def ApiCreatedResponse(description: Optional[str] = None, schema: Schema = None, example: Any = None):
    return ApiResponse(
        status=201,
        response=Response(
            description or 'Success response',
            content={
                'application/json': MediaType(
                    schema=schema or Schema(),
                    example=example
                )
            }
        )
    )


def ApiNotFoundResponse(description: Optional[str] = None, schema: Schema = None, example: Any = None):
    return ApiResponse(
        status=404,
        response=Response(
            description or 'Not Found',
            content={
                'application/json': MediaType(
                    schema=schema or Schema(),
                    example=example
                )
            }
        )
    )


def ApiParameter(param: Parameter):
    return SetMetadata(key='__openapi__parameters', data=[param], as_list=True)


def ApiTags(tags: Union[str, list[str]]):
    if isinstance(tags, str):
        tags = [tags]
    return SetMetadata(key='__openapi__tags', data=tags, as_list=True)


def ApiId(api_id: str):
    return SetMetadata(key='__openapi__operation_id', data=api_id)


def ApiBasicAuth():
    return SetMetadata(key='__openapi__security', data=[SecurityRequirement(
        name='basicAuth',
        value=[
            'basicAuth'
        ]
    )], as_list=True)


def ApiBearerAuth():
    return SetMetadata(key='__openapi__security', data=[SecurityRequirement(
        name='bearer',
        value=[
            'bearer'
        ]
    )], as_list=True)


def ApiSecurity(security: SecurityRequirement):
    return SetMetadata(key='__openapi__security', data=[security], as_list=True)

# TODO : Add more openapi decorator
