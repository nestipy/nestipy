from nestipy.core.providers.async_local_storage import AsyncLocalStorage
from nestipy.core.providers.background import BackgroundTask, BackgroundTasks
from nestipy.core.providers.discover import DiscoverService

from .adapter.http_adapter import HttpAdapter
from .application import NestipyApplication, NestipyConfig
from .constant import AppKey
from .context.execution_context import ArgumentHost, ExecutionContext, HttpArgumentHost
from .factory import NestipyFactory
from .health import HealthController, HealthRegistry, ReadyState
from .middleware import MiddlewareConsumer
from .on_application_bootstrap import OnApplicationBootstrap
from .on_application_shutdown import OnApplicationShutdown
from .on_destroy import OnDestroy
from .on_init import OnInit
from .on_module_destroy import OnModuleDestroy
from .on_module_init import OnModuleInit
from .platform import BlackSheepApplication, FastApiApplication
from .template import MinimalJinjaTemplateEngine

try:
    from .microservice import NestipyConnectMicroservice, NestipyMicroservice
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
