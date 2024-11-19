from .adapter.http_adapter import HttpAdapter
from .constant import AppKey
from .context.execution_context import ExecutionContext, ArgumentHost, HttpArgumentHost
from .discover import DiscoverService
from .middleware import MiddlewareConsumer
from .nestipy_application import NestipyApplication, NestipyConfig
from .nestipy_factory import NestipyFactory
from .on_init import OnInit
from .on_destroy import OnDestroy
from .platform import FastApiApplication, BlackSheepApplication
from .template import MinimalJinjaTemplateEngine

try:
    from .nestipy_microservice import NestipyMicroservice, NestipyConnectMicroservice
except ImportError:
    NestipyMicroservice = None
    NestipyConnectMicroservice = None

from .background import BackgroundTask, BackgroundTasks

__all__ = [
    "NestipyFactory",
    "NestipyApplication",
    "NestipyConfig",
    "HttpAdapter",
    "ExecutionContext",
    "ArgumentHost",
    "HttpArgumentHost",
    "FastApiApplication",
    "BlackSheepApplication",
    "MinimalJinjaTemplateEngine",
    "AppKey",
    "MiddlewareConsumer",
    "DiscoverService",
    "OnInit",
    "OnDestroy",
    "NestipyMicroservice",
    "NestipyConnectMicroservice",
    "BackgroundTask",
    "BackgroundTasks",
]
