from dataclasses import dataclass

from pydantic import create_model

from .decorator_v2 import (
    ApiAcceptedResponse,
    ApiBadRequestResponse,
    ApiBasicAuth,
    ApiBearerAuth,
    ApiBody,
    ApiCallbacks,
    ApiConflictResponse,
    ApiConsumer,
    ApiCookie,
    ApiCreatedResponse,
    ApiDeprecated,
    ApiDescription,
    ApiExclude,
    ApiExcludeEndpoint,
    ApiExternalDocs,
    ApiExtraModels,
    ApiForbiddenResponse,
    ApiHeader,
    ApiId,
    ApiInternalServerErrorResponse,
    ApiNoContentResponse,
    ApiNotFoundResponse,
    ApiOkResponse,
    ApiOperation,
    ApiParam,
    ApiParameter,
    ApiPath,
    ApiQuery,
    ApiResponse,
    ApiSecurity,
    ApiServer,
    ApiServers,
    ApiServiceUnavailableResponse,
    ApiSummary,
    ApiTags,
    ApiTooManyRequestsResponse,
    ApiUnauthorizedResponse,
    ApiUnprocessableEntityResponse,
)
from .document_builder import DocumentBuilder
from .swagger_module import SwaggerModule


def ApiSchema(cls):
    data_cls = dataclass(cls)
    fields = {}
    for field in data_cls.__dataclass_fields__.values():
        fields[field.name] = (field.type, ...)
    # Schema
    return create_model(data_cls.__name__, **fields)


if __name__ == "__main__":
    # Example usage:
    @ApiSchema
    class TestDto:
        name: str

    @ApiSchema
    class CreateCatDto:
        name: str
        age: int
        breed: str
        test: TestDto


__all__ = [
    "DocumentBuilder",
    "SwaggerModule",
    "ApiResponse",
    "ApiCreatedResponse",
    "ApiOkResponse",
    "ApiNotFoundResponse",
    "ApiBadRequestResponse",
    "ApiUnauthorizedResponse",
    "ApiForbiddenResponse",
    "ApiConflictResponse",
    "ApiUnprocessableEntityResponse",
    "ApiTooManyRequestsResponse",
    "ApiInternalServerErrorResponse",
    "ApiServiceUnavailableResponse",
    "ApiNoContentResponse",
    "ApiAcceptedResponse",
    "ApiTags",
    "ApiId",
    "ApiBody",
    "ApiParameter",
    "ApiHeader",
    "ApiPath",
    "ApiParam",
    "ApiQuery",
    "ApiCookie",
    "ApiSummary",
    "ApiDescription",
    "ApiDeprecated",
    "ApiOperation",
    "ApiExternalDocs",
    "ApiServer",
    "ApiServers",
    "ApiCallbacks",
    "ApiExtraModels",
    "ApiBearerAuth",
    "ApiBasicAuth",
    "ApiSecurity",
    "ApiExclude",
    "ApiExcludeEndpoint",
    "ApiConsumer",
]
