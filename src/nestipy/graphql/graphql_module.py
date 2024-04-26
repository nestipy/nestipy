import dataclasses
from typing import Literal

from nestipy.common.decorator import Module
from nestipy_dynamic_module import ConfigurableModuleBuilder
from nestipy_ioc import Inject


@dataclasses.dataclass
class GraphqlOption:
    url: str = '/graphql'
    ide: Literal['default', 'graphiql'] = 'default'


ConfigurableModuleClass, CONFIG_MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[GraphqlOption]().set_method(
    'for_root').build()


@Module()
class GraphqlModule(ConfigurableModuleClass):
    config: Inject[CONFIG_MODULE_OPTION_TOKEN]
