import dataclasses
import inspect
from enum import Enum
from typing import Union, Optional, Any, Type, Callable, Dict

from pydantic import TypeAdapter, BaseModel

from nestipy.metadata import SetMetadata
from .openapi_docs.v3 import (
    RequestBody,
    Response,
    Parameter,
    ParameterLocation,
    Header,
    Reference,
    ExternalDocs,
    Server,
    Callback,
)
from .openapi_docs.v3 import SecurityRequirement, MediaType, Schema


class ApiConsumer(Enum):
    JSON = "application/json"
    MULTIPART = "multipart/form-data"
    X_WWW_FORM_URLENCODED = "application/x-www-form-urlencoded"


def _dict_to_dataclass(data: dict[str, Any], cls: Any) -> Any:
    field_names = {field.name for field in dataclasses.fields(cls)}
    filtered_data = {key: value for key, value in data.items() if key in field_names}
    return cls(**filtered_data)


def _get_json_of_body(body: Optional[Union[BaseModel, Type]]):
    content: dict = {}
    if body is None:
        return content
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


# API BODY


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


def ApiParameter(param: Parameter):
    return SetMetadata(key="__openapi__parameters", data=[param], as_list=True)


def ApiHeader(name: str, description: Optional[str] = None, required: bool = True):
    return ApiParameter(
        Parameter(
            name=name,
            description=description,
            in_=ParameterLocation.HEADER,
            required=required,
        )
    )


def ApiPath(name: str, description: Optional[str] = None):
    return ApiParameter(
        Parameter(
            name=name,
            description=description,
            in_=ParameterLocation.PATH,
            required=True,
        )
    )


def ApiQuery(name: str, description: Optional[str] = None, required: bool = False):
    return ApiParameter(
        Parameter(
            name=name,
            description=description,
            in_=ParameterLocation.QUERY,
            required=required,
        )
    )


#  API Response
def ApiResponse(
    status: int,
    response: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
    headers: Optional[Dict[str, Union[Header, Reference]]] = None,
    consumer: ApiConsumer = ApiConsumer.JSON,
):
    content = _get_json_of_body(response)
    response_body = Response(
        headers=headers,
        description=description,
        content={
            consumer.value: MediaType(
                schema=_dict_to_dataclass(content, Schema), example=example
            )
        },
    )
    return _ApiResponse(status, response_body)

def ApiBadRequestResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    if schema is None:
        try:
            from nestipy.common.openapi_error import OpenApiErrorResponse

            schema = OpenApiErrorResponse
        except Exception:
            schema = None
    return ApiResponse(
        status=400, description=description, response=schema, example=example
    )


def _ApiResponse(status: int, response: Response):
    return SetMetadata(
        key="__openapi__responses", data={status: response}, as_dict=True
    )


def ApiExclude():
    return SetMetadata(key="__openapi__hidden", data=True)


def ApiOkResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=200, description=description, response=schema, example=example
    )


def ApiCreatedResponse(
    schema: Union[BaseModel, Type, None] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=201, description=description, response=schema, example=example
    )


def ApiNotFoundResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=404, description=description, response=schema, example=example
    )


# API INFO


def ApiTags(tags: Union[str, list[str]]):
    if isinstance(tags, str):
        tags = [tags]
    return SetMetadata(key="__openapi__tags", data=tags, as_list=True)


def ApiId(api_id: str):
    return SetMetadata(key="__openapi__operation_id", data=api_id)


def ApiSummary(summary: str):
    return SetMetadata(key="__openapi__summary", data=summary)


def ApiDescription(description: str):
    return SetMetadata(key="__openapi__description", data=description)


def ApiDeprecated(deprecated: bool = True):
    return SetMetadata(key="__openapi__deprecated", data=deprecated)


def ApiOperation(
    summary: Optional[str] = None,
    description: Optional[str] = None,
    deprecated: Optional[bool] = None,
    operation_id: Optional[str] = None,
):
    decorators: list = []
    if summary is not None:
        decorators.append(ApiSummary(summary))
    if description is not None:
        decorators.append(ApiDescription(description))
    if deprecated is not None:
        decorators.append(ApiDeprecated(deprecated))
    if operation_id is not None:
        decorators.append(ApiId(operation_id))

    def wrapper(cls: Union[Type, Callable]):
        for deco in decorators:
            cls = deco(cls)
        return cls

    return wrapper


def ApiExternalDocs(url: str, description: Optional[str] = None):
    return SetMetadata(
        key="__openapi__external_docs", data=ExternalDocs(url=url, description=description)
    )


def ApiServer(url: str, description: Optional[str] = None, variables: Optional[dict] = None):
    return SetMetadata(
        key="__openapi__servers",
        data=[Server(url=url, description=description, variables=variables)],
        as_list=True,
    )


def ApiServers(servers: list[Server]):
    return SetMetadata(key="__openapi__servers", data=servers, as_list=True)


def ApiCallbacks(callbacks: Dict[str, Callback]):
    return SetMetadata(key="__openapi__callbacks", data=callbacks, as_dict=True)


def ApiExtraModels(*models: Union[BaseModel, Type]):
    defs: dict = {}
    for model in models:
        content = _get_json_of_body(model)
        if "$defs" in content:
            defs.update(content["$defs"])
        title = content.get("title") if isinstance(content, dict) else None
        if title and title not in defs:
            schema = {k: v for k, v in content.items() if k != "$defs"}
            defs[title] = schema
    return SetMetadata(key="__openapi__schemas", data=defs, as_dict=True)


# SECURITY


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


def ApiExcludeEndpoint():
    return ApiExclude()


# TODO : Add more openapi decorator
def ApiParam(name: str, description: Optional[str] = None):
    return ApiPath(name=name, description=description)


def ApiCookie(name: str, description: Optional[str] = None, required: bool = False):
    return ApiParameter(
        Parameter(
            name=name,
            description=description,
            in_=ParameterLocation.COOKIE,
            required=required,
        )
    )

def ApiUnauthorizedResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=401, description=description, response=schema, example=example
    )


def ApiForbiddenResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=403, description=description, response=schema, example=example
    )


def ApiConflictResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=409, description=description, response=schema, example=example
    )


def ApiUnprocessableEntityResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=422, description=description, response=schema, example=example
    )


def ApiTooManyRequestsResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=429, description=description, response=schema, example=example
    )


def ApiInternalServerErrorResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=500, description=description, response=schema, example=example
    )


def ApiServiceUnavailableResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=503, description=description, response=schema, example=example
    )


def ApiNoContentResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=204, description=description, response=schema, example=example
    )


def ApiAcceptedResponse(
    schema: Optional[Union[BaseModel, Type]] = None,
    description: Optional[str] = None,
    example: Any = None,
):
    return ApiResponse(
        status=202, description=description, response=schema, example=example
    )
