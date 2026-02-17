import dataclasses
from datetime import timedelta
from typing import Literal, Annotated, Optional, Sequence, Callable, Any, Union, Mapping

from nestipy.core.security.cors import CorsOptions

from nestipy.common.decorator import Module
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import Inject


@dataclasses.dataclass
class ASGIOption:
    allow_queries_via_get: bool = True
    graphiql: Optional[bool] = None
    graphql_ide: Optional[str] = None
    keep_alive: bool = False
    keep_alive_interval: float = 1
    subscription_protocols: Optional[Sequence[str]] = None
    connection_init_wait_timeout: timedelta = timedelta(minutes=1)
    multipart_uploads_enabled: bool = False


@dataclasses.dataclass
class SchemaOption:
    directives: Optional[Sequence[Any]] = None
    types: Optional[Sequence[Any]] = None
    extensions: Optional[Sequence[Any]] = None
    execution_context_class: Optional[type] = None
    config: Optional[Any] = None
    scalar_overrides: Optional[Mapping[object, Any]] = None
    schema_directives: Optional[Sequence[Any]] = None


@dataclasses.dataclass
class GraphqlOption:
    url: str = "/graphql"
    cors: bool | CorsOptions | dict[str, Any] = True
    auto_schema_file: Optional[str] = None
    ide: Literal["default", "graphiql", "apollo-sandbox"] = "graphiql"
    schema_option: Optional[Union[SchemaOption, dict[str, Any]]] = None
    asgi_option: Optional[Union[ASGIOption, dict[str, Any]]] = None
    context_callback: Optional[Callable[[...], dict]] = None
    schema: Optional[Any] = None
    schema_factory: Optional[Callable[..., Any]] = None

    def __post_init__(self):
        if self.ide not in ["default", "graphiql", "apollo-sandbox"]:
            raise ValueError("ide value must be one of 'default', 'graphiql'")


ConfigurableModuleClass, CONFIG_MODULE_OPTION_TOKEN = (
    ConfigurableModuleBuilder[GraphqlOption]().set_method("for_root").build()
)


@Module()
class GraphqlModule(ConfigurableModuleClass):
    config: Annotated[GraphqlOption, Inject(CONFIG_MODULE_OPTION_TOKEN)]
