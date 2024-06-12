import dataclasses
from typing import Literal, Annotated

from nestipy.common.decorator import Module
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import Inject


@dataclasses.dataclass
class GraphqlOption:
    url: str = '/graphql'
    ide: Literal['default', 'graphiql'] | None = 'default'


ConfigurableModuleClass, CONFIG_MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[GraphqlOption]().set_method(
    'for_root').build()


@Module()
class GraphqlModule(ConfigurableModuleClass):
    config: Annotated[GraphqlOption, Inject(CONFIG_MODULE_OPTION_TOKEN)]
