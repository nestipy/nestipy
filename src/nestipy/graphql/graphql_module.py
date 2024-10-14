import dataclasses
from datetime import timedelta
from typing import Literal, Annotated, Optional, Sequence, Callable

from nestipy.common.decorator import Module
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import Inject


@dataclasses.dataclass
class AsgiOption:
    allow_queries_via_get: bool = True
    keep_alive: bool = False
    keep_alive_interval: float = 1
    debug: bool = False
    subscription_protocols: Sequence[str] = None
    connection_init_wait_timeout: timedelta = timedelta(minutes=1)


@dataclasses.dataclass
class GraphqlOption:
    url: str = "/graphql"
    cors: bool = True
    auto_schema_file: Optional[str] = None
    ide: Literal["default", "graphiql"] = "default"
    schema_option: Optional[dict] = None
    asgi_option: Optional[AsgiOption] = None
    context_callback: Optional[Callable[[...], dict]] = None


ConfigurableModuleClass, CONFIG_MODULE_OPTION_TOKEN = (
    ConfigurableModuleBuilder[GraphqlOption]().set_method("for_root").build()
)


@Module()
class GraphqlModule(ConfigurableModuleClass):
    config: Annotated[GraphqlOption, Inject(CONFIG_MODULE_OPTION_TOKEN)]
