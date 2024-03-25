import dataclasses
from typing import Literal

from nestipy.common import Module
from nestipy.common.dynamic_module.builder import ConfigurableModuleBuilder
from nestipy.common.metadata.provider_token import ProviderToken
from nestipy.types_ import Inject


@dataclasses.dataclass
class GraphqlOption:
    url: str = '/graphql'
    ide: Literal['default', 'graphiql'] = 'default'


ConfigurableModuleClass, CONFIG_MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[GraphqlOption]().set_method(
    'for_root').build()


@Module()
class GraphqlModule(ConfigurableModuleClass):
    config: Inject[ProviderToken(CONFIG_MODULE_OPTION_TOKEN)]
