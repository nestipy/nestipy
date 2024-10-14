from dataclasses import dataclass

from nestipy.common.decorator.class_ import Module
from nestipy.dynamic_module import ConfigurableModuleBuilder, DynamicModule
from nestipy.ioc.provider import ModuleProviderDict
from .base import MicroserviceOption
from .factory import ClientModuleFactory


@dataclass
class ClientsConfig:
    name: str
    option: MicroserviceOption


ConfigurableModuleClass, CLIENT_OPTION = ConfigurableModuleBuilder[
    list[ClientsConfig]
]().build()


@Module()
class ClientsModule(ConfigurableModuleClass):
    @classmethod
    def register(cls, option: list[ClientsConfig]):
        dynamic_module: DynamicModule = getattr(ConfigurableModuleClass, "register")(
            option
        )
        providers = []
        for opt in option:
            providers.append(
                ModuleProviderDict(
                    token=opt.name, value=ClientModuleFactory.create(opt.option)
                )
            )
        dynamic_module.providers = dynamic_module.providers + providers
        dynamic_module.is_global = True
        return dynamic_module
