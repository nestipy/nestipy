from typing import Optional, Awaitable, Callable, Union, Type

from nestipy.common.decorator import Module
from .config_builder import ConfigurableModuleClass, ConfigOption
from .config_service import ConfigService


@Module(
    providers=[ConfigService],
    exports=[ConfigService],
)
class ConfigModule(ConfigurableModuleClass):

    @classmethod
    def for_root(cls, option: ConfigOption | None = ConfigOption(), is_global: bool = False):
        module = super().for_root(option)  # Call on cls to preserve subclass
        module.is_global = option.is_global or is_global
        return module

    @classmethod
    def for_root_async(
        cls,
        value: Optional[ConfigOption] = None,
        factory: Callable[..., Union[Awaitable[ConfigOption], ConfigOption]] = None,
        existing: Union[Type, str] = None,
        use_class: Type = None,
        inject: list = None,
        imports: list = None,
        extras: dict = None,
        is_global: bool = False
    ):
        module = super().for_root_async(
            value=value,
            factory=factory,
            existing=existing,
            use_class=use_class,
            inject=inject,
            imports=imports,
            extras=extras
        )
        module.is_global = is_global
        return module
