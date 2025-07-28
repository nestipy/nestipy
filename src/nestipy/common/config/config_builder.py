from dataclasses import dataclass, field
from typing import Callable

from nestipy.dynamic_module import ConfigurableModuleBuilder, DynamicModule


@dataclass
class ConfigOption:
    folder: str = './'
    is_global: bool = False
    ignore_env_file: bool = False
    load: list[Callable] = field(default_factory=lambda: [])


def extras_callback(dynamic_module: DynamicModule, extras: dict):
    is_global = extras.get('is_global')
    if is_global is not None:
        dynamic_module.is_global = is_global


ConfigurableModuleClass, CONFIG_OPTION = ConfigurableModuleBuilder[ConfigOption]().set_extras(
    {'is_global': False, }, extras_callback).set_method(
    'for_root').build()
