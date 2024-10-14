from dataclasses import dataclass

from pydantic import create_model

from .decorator import ApiBearerAuth, ApiBasicAuth, ApiSecurity, NoSwagger
from .decorator import (
    ApiResponse,
    ApiCreatedResponse,
    ApiOkResponse,
    ApiNotFoundResponse,
    ApiConsumer,
)
from .decorator import ApiTags, ApiId, ApiBody, ApiParameter
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
    "ApiTags",
    "ApiId",
    "ApiBody",
    "ApiParameter",
    "ApiBearerAuth",
    "ApiBasicAuth",
    "ApiSecurity",
    "NoSwagger",
    "ApiConsumer",
]
