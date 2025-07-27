from dataclasses import asdict
from typing import Literal, Annotated

from nestipy.common.decorator import Module, Injectable
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import ModuleProviderDict, Inject
from nestipy.metadata import Reflect

Config = dict[Literal["folder"], str]
ConfigurableModuleClass, CONFIG_MODULE_OPTION_TOKEN = (
    ConfigurableModuleBuilder[Config]().set_method("for_root").build()
)


@Injectable()
class ConfigService:
    token: Annotated[str, Inject(CONFIG_MODULE_OPTION_TOKEN)]


@Module(
    providers=[ConfigService, ModuleProviderDict(value="hello", token="MyProvider")],
    exports=[ConfigService],
    is_global=True,
)
class ConfigModule(ConfigurableModuleClass): ...


if __name__ == "__main__":
    d = ConfigModule.for_root({"folder": "./config"})
    meta = Reflect.get(d)
    print(meta, {k: v for k, v in asdict(d).items() if k != "module"})

__all__ = ["ConfigService", "ConfigModule"]
