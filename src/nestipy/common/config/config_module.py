from typing import Awaitable, Callable, Optional, Type, Union

from nestipy.common.decorator import Module

from .config_builder import ConfigOption, ConfigurableModuleClass
from .config_service import ConfigService


@Module(
    providers=[ConfigService],
    exports=[ConfigService],
)
class ConfigModule(ConfigurableModuleClass):
    @classmethod
    def for_root(cls, option: ConfigOption = ConfigOption(), is_global: bool = False):
        module = cls.register(option)  # Call on cls to preserve subclass
        module.is_global = option.is_global or is_global
        return module

    @classmethod
    def for_root_async(
        cls,
        value: Optional[ConfigOption] = None,
        factory: Union[Callable[..., Awaitable[ConfigOption]], None] = None,
        existing: Union[Type, str, None] = None,
        use_class: Union[Type, None] = None,
        inject: Union[list, None] = None,
        imports: Union[list, None] = None,
        extras: Union[dict, None] = None,
        is_global: bool = False,
    ):
        module = cls.register_async(
            value=value,
            factory=factory,
            existing=existing,
            use_class=use_class,
            inject=inject,
            imports=imports,
            extras=extras,
        )
        module.is_global = is_global
        return module
