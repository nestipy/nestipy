import dataclasses
import inspect
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, Union

from pydantic import BaseModel, TypeAdapter

from nestipy.metadata import SetMetadata

from .openapi_docs.v3 import (
    Callback,
    Encoding,
    Example,
    ExternalDocs,
    MediaType,
    Parameter,
    ParameterLocation,
    Reference,
    RequestBody,
    Response,
    Schema,
    SecurityRequirement,
    Server,
)


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


@dataclasses.dataclass
class ApiBody(RequestBody):
    body: Union[BaseModel, Type, None] = dataclasses.field(default=None)
    required: bool = dataclasses.field(default=True)
    consumer: Union[ApiConsumer, None] = dataclasses.field(default=ApiConsumer.JSON)
    content: Optional[Dict[str, MediaType]] = dataclasses.field(default=None)

    def __call__(self, cls: Union[Callable, Type]):
        content = _get_json_of_body(self.body)
        self.content = {
            self.consumer.value: MediaType(
                schema=_dict_to_dataclass(content, Schema),
            )
        }
        self.consumer = None
        self.body = None
        decorator = SetMetadata(key="__openapi__request_body", data=self)
        return _create_decorator_to_add_schema_ref(decorator, self.content)(cls)


# API PARAMETER


@dataclasses.dataclass
class ApiParameter(Parameter):
    def __call__(self, cls: Union[Callable, Type]) -> Union[Callable, Type]:
        return SetMetadata(key="__openapi__parameters", data=[self], as_list=True)(cls)


@dataclasses.dataclass
class ApiHeader(ApiParameter):
    in_: ParameterLocation = dataclasses.field(default=ParameterLocation.HEADER)


@dataclasses.dataclass
class ApiPath(ApiParameter):
    in_: ParameterLocation = dataclasses.field(default=ParameterLocation.PATH)
    required: bool = dataclasses.field(default=True)


@dataclasses.dataclass
class ApiQuery(ApiParameter):
    in_: ParameterLocation = dataclasses.field(default=ParameterLocation.QUERY)


@dataclasses.dataclass
class ApiParam(ApiPath): ...


@dataclasses.dataclass
class ApiCookie(ApiParameter):
    in_: str = dataclasses.field(default=ParameterLocation.COOKIE)


#  API Exclude
def ApiExclude():
    return SetMetadata(key="__openapi__hidden", data=True)


def ApiExcludeEndpoint():
    return ApiExclude()


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
        key="__openapi__external_docs",
        data=ExternalDocs(url=url, description=description),
    )


def ApiServer(
    url: str, description: Optional[str] = None, variables: Optional[dict] = None
):
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


#  API Response
def _ApiResponse(status: int, response: Response):
    return SetMetadata(
        key="__openapi__responses", data={status: response}, as_dict=True
    )


@dataclasses.dataclass
class ApiResponse(Response):
    schema: Optional[Union[BaseModel, Type]] = None
    status: int = 200
    consumer: Union[ApiConsumer, None] = dataclasses.field(default=ApiConsumer.JSON)
    example: Any = None
    examples: Dict[str, Example | Reference] | None = None
    encoding: Dict[str, Encoding] | None = None

    def __call__(self, cls: Any) -> Any:
        content = _get_json_of_body(self.schema)
        self.content = {
            self.consumer.value: MediaType(
                schema=_dict_to_dataclass(content, Schema),
                example=self.example,
                examples=self.examples,
                encoding=self.encoding,
            )
        }
        self.schema = None
        self.consumer = None
        self.example = None
        self.examples = None
        self.encoding = None
        return _ApiResponse(self.status, self)(cls)


@dataclasses.dataclass
class ApiBadRequestResponse(ApiResponse):
    status: int = dataclasses.field(default=400)
    schema: Optional[Union[BaseModel, Type]] = dataclasses.field(default=None)


@dataclasses.dataclass
class ApiOkResponse(ApiResponse):
    status: int = dataclasses.field(default=200)


@dataclasses.dataclass
class ApiCreatedResponse(ApiResponse):
    status: int = dataclasses.field(default=201)


@dataclasses.dataclass
class ApiNotFoundResponse(ApiResponse):
    status: int = dataclasses.field(default=404)


@dataclasses.dataclass
class ApiUnauthorizedResponse(ApiResponse):
    status: int = dataclasses.field(default=401)


@dataclasses.dataclass
class ApiForbiddenResponse(ApiResponse):
    status: int = dataclasses.field(default=403)


@dataclasses.dataclass
class ApiConflictResponse(ApiResponse):
    status: int = dataclasses.field(default=409)


@dataclasses.dataclass
class ApiUnprocessableEntityResponse(ApiResponse):
    status: int = dataclasses.field(default=422)


@dataclasses.dataclass
class ApiTooManyRequestsResponse(ApiResponse):
    status: int = dataclasses.field(default=429)


@dataclasses.dataclass
@dataclasses.dataclass
class ApiInternalServerErrorResponse(ApiResponse):
    status: int = dataclasses.field(default=500)


@dataclasses.dataclass
@dataclasses.dataclass
class ApiServiceUnavailableResponse(ApiResponse):
    status: int = dataclasses.field(default=503)


@dataclasses.dataclass
class ApiNoContentResponse(ApiResponse):
    status: int = dataclasses.field(default=204)


@dataclasses.dataclass
class ApiAcceptedResponse(ApiResponse):
    status: int = dataclasses.field(default=202)


# TODO : Add more openapi decorator
