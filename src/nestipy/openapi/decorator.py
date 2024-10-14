import dataclasses
import inspect
from enum import Enum
from typing import Union, Optional, Any, Type, Callable

from pydantic import TypeAdapter, BaseModel

from nestipy.metadata import SetMetadata
from .openapi_docs.v3 import RequestBody, Response, Parameter
from .openapi_docs.v3 import SecurityRequirement, MediaType, Schema


class ApiConsumer(Enum):
    JSON = "application/json"
    MULTIPART = "multipart/form-data"
    X_WWW_FORM_URLENCODED = "application/x-www-form-urlencoded"


def _dict_to_dataclass(data: dict[str, Any], cls: Any) -> Any:
    field_names = {field.name for field in dataclasses.fields(cls)}
    filtered_data = {key: value for key, value in data.items() if key in field_names}
    return cls(**filtered_data)


def _get_json_of_body(body: Union[BaseModel, Type]):
    content: dict = {}
    ref_template = "#/components/schemas/{model}"
    if dataclasses.is_dataclass(body):
        content = TypeAdapter(body).json_schema(ref_template=ref_template)
    elif inspect.isclass(body) and issubclass(body, BaseModel):
        content = body.model_json_schema(ref_template=ref_template)
    return content


def _create_decorator_to_add_schema_ref(decorator: Callable, content: dict):
    if "$defs" not in content:
        return decorator

    def update_decorator(cls: Union[Type, Callable]):
        new_cls = decorator(cls)
        class_decorated = SetMetadata(
            key="__openapi__schemas", as_dict=True, data=content["$defs"]
        )(new_cls)
        return class_decorated

    return update_decorator


def ApiBody(
    body: Union[BaseModel, Type, None] = None, consumer: ApiConsumer = ApiConsumer.JSON
):
    content = _get_json_of_body(body)
    data_body: RequestBody = RequestBody(
        required=True,
        content={
            consumer.value: MediaType(
                schema=_dict_to_dataclass(content, Schema),
            )
        },
    )
    decorator = SetMetadata(key="__openapi__request_body", data=data_body)
    return _create_decorator_to_add_schema_ref(decorator, content)


def ApiResponse(
    status: int,
    response: Union[BaseModel, Type] = None,
    description: str = None,
    example: Any = None,
    consumer: ApiConsumer = ApiConsumer.JSON,
):
    content = _get_json_of_body(response)
    response_body = Response(
        description=description,
        content={
            consumer.value: MediaType(
                schema=_dict_to_dataclass(content, Schema), example=example
            )
        },
    )
    return _ApiResponse(status, response_body)


def _ApiResponse(status: int, response: Response):
    return SetMetadata(
        key="__openapi__responses", data={status: response}, as_dict=True
    )


def NoSwagger():
    return SetMetadata(key="__openapi__no_swagger", data=True)


def ApiOkResponse(
    schema: Union[BaseModel, Type] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=200, description=description, response=schema, example=example
    )


def ApiCreatedResponse(
    schema: Union[BaseModel, Type] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=201, description=description, response=schema, example=example
    )


def ApiNotFoundResponse(
    schema: Union[BaseModel, Type] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=404, description=description, response=schema, example=example
    )


def ApiParameter(param: Parameter):
    return SetMetadata(key="__openapi__parameters", data=[param], as_list=True)


def ApiTags(tags: Union[str, list[str]]):
    if isinstance(tags, str):
        tags = [tags]
    return SetMetadata(key="__openapi__tags", data=tags, as_list=True)


def ApiId(api_id: str):
    return SetMetadata(key="__openapi__operation_id", data=api_id)


def ApiBasicAuth():
    return SetMetadata(
        key="__openapi__security",
        data=[SecurityRequirement(name="basicAuth", value=["basicAuth"])],
        as_list=True,
    )


def ApiBearerAuth():
    return SetMetadata(
        key="__openapi__security",
        data=[SecurityRequirement(name="bearer", value=["bearer"])],
        as_list=True,
    )


def ApiSecurity(security: SecurityRequirement):
    return SetMetadata(key="__openapi__security", data=[security], as_list=True)


# TODO : Add more openapi decorator
