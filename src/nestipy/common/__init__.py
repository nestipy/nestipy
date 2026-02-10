from .decorator import (
    Module,
    Controller,
    Injectable,
    Scope,
    Route,
    Get,
    Post,
    Patch,
    Put,
    Delete,
    apply_decorators,
)
from .exception import (
    HttpException,
    HttpStatusMessages,
    HttpStatus,
    UseFilters,
    Catch,
    ExceptionKey,
    ExceptionFilter,
)
from .guards import CanActivate, UseGuards
from .http_ import Request, Response, Websocket, UploadFile
from .interceptor import NestipyInterceptor, UseInterceptors
from .pipes import (
    PipeTransform,
    PipeArgumentMetadata,
    UsePipes,
    ParseIntPipe,
    ParseFloatPipe,
    ParseBoolPipe,
    ParseUUIDPipe,
    ParseJsonPipe,
    DefaultValuePipe,
    ValidationPipe,
)
from .logger import logger, console
from .constant import NESTIPY_SCOPE_ATTR, SCOPE_SINGLETON, SCOPE_TRANSIENT, SCOPE_REQUEST
from .openapi_error import OpenApiErrorResponse, OpenApiErrorDetail
from .middleware import cors, NestipyMiddleware, session, SessionOption, helmet
from .middleware import cookie_session, SessionCookieOption, SessionStore
from .template import Render, TemplateEngine


def __getattr__(name: str):
    if name in {"ConfigModule", "ConfigService"}:
        from .config import ConfigModule, ConfigService

        return ConfigModule if name == "ConfigModule" else ConfigService
    if name == "ModuleProviderDict":
        from nestipy.ioc.provider import ModuleProviderDict

        return ModuleProviderDict
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = [
    "ConfigModule",
    "ConfigService",
    "Module",
    "Controller",
    "Injectable",
    "Scope",
    "Route",
    "Get",
    "Post",
    "Put",
    "Patch",
    "Delete",
    "HttpException",
    "HttpStatusMessages",
    "HttpStatus",
    "UseFilters",
    "Catch",
    "ExceptionKey",
    "ExceptionFilter",
    "CanActivate",
    "UseGuards",
    "Response",
    "Request",
    "Websocket",
    "UploadFile",
    "NestipyInterceptor",
    "UseInterceptors",
    "PipeTransform",
    "PipeArgumentMetadata",
    "UsePipes",
    "ParseIntPipe",
    "ParseFloatPipe",
    "ParseBoolPipe",
    "ParseUUIDPipe",
    "ParseJsonPipe",
    "DefaultValuePipe",
    "ValidationPipe",
    "cors",
    "helmet",
    "NestipyMiddleware",
    "Render",
    "TemplateEngine",
    "ModuleProviderDict",
    "session",
    "SessionOption",
    "logger",
    "console",
    "apply_decorators",
    "cookie_session",
    "SessionStore",
    "SessionCookieOption",
    "NESTIPY_SCOPE_ATTR",
    "SCOPE_SINGLETON",
    "SCOPE_TRANSIENT",
    "SCOPE_REQUEST",
    "OpenApiErrorResponse",
    "OpenApiErrorDetail",
]
