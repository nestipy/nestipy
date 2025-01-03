from dataclasses import dataclass
from typing import Any, cast

from nestipy.dynamic_module import ConfigurableModuleBuilder, DynamicModule


@dataclass
class EventOption:
    pass


def extract_callback(dynamic_module: DynamicModule, extras: dict[str, Any]):
    if extras.get("is_global"):
        dynamic_module.is_global = cast(bool, extras.get("is_global", False))


ConfigurableClassBuilder, EVENT_CONFIG = (
    ConfigurableModuleBuilder[EventOption]().set_extras({}, extract_callback).build()
)
