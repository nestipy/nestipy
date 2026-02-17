from nestipy.core.providers.async_local_storage import AsyncLocalStorage
from nestipy.core.providers.background import BackgroundTask, BackgroundTasks
from nestipy.core.providers.discover import DiscoverService
from .adapter.http_adapter import HttpAdapter
from .constant import AppKey
from .context.execution_context import ExecutionContext, ArgumentHost, HttpArgumentHost
from .middleware import MiddlewareConsumer
from .nestipy_application import NestipyApplication, NestipyConfig
from .nestipy_factory import NestipyFactory
from .health import HealthRegistry, HealthController, ReadyState
from .on_application_bootstrap import OnApplicationBootstrap
from .on_application_shutdown import OnApplicationShutdown
from .on_destroy import OnDestroy
from .on_init import OnInit
from .on_module_destroy import OnModuleDestroy
from .on_module_init import OnModuleInit
from .platform import FastApiApplication, BlackSheepApplication
from .template import MinimalJinjaTemplateEngine

try:
    from .nestipy_microservice import NestipyMicroservice, NestipyConnectMicroservice
except ImportError:
    NestipyMicroservice = None
    NestipyConnectMicroservice = None

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
    "AsyncLocalStorage",
    "OnInit",
    "OnDestroy",
    "OnModuleInit",
    "OnModuleDestroy",
    "OnApplicationBootstrap",
    "OnApplicationShutdown",
    "NestipyMicroservice",
    "NestipyConnectMicroservice",
    "BackgroundTask",
    "BackgroundTasks",
    "HealthRegistry",
    "HealthController",
    "ReadyState",
]
