from dataclasses import asdict
from typing import Literal

from nestipy.common.decorator import Module, Injectable
from nestipy.common.provider import ModuleProviderDict
from nestipy.types_ import Inject
from .builder import ConfigurableModuleBuilder
from ..metadata.provide import Provide
from ..metadata.reflect import Reflect

Config = dict[Literal['folder'], str]
ConfigurableModuleClass, CONFIG_MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[Config]().set_method('for_root').build()


@Injectable()
class ConfigService:
    token: Inject[Provide(CONFIG_MODULE_OPTION_TOKEN)]


@Module(
    providers=[
        ConfigService,
        ModuleProviderDict(value='hello', provide='MyProvider')
    ]
)
class ConfigModule(ConfigurableModuleClass):
    ...


if __name__ == '__main__':
    d = ConfigModule.for_root({'folder': './config'})
    meta = Reflect.get(d)
    print(meta, {k: v for k, v in asdict(d).items() if k != 'module'})
