from typing import Optional

from ...common.decorator.module import Module
from .config_service import ConfigService
from .constant import CONFIG_MODULE_TOKEN
from ..dynamic_module.dynamic_module import DynamicModule


@Module(providers=[ConfigService], exports=[ConfigService], is_global=True)
class ConfigModule(DynamicModule):

    @classmethod
    def for_root(cls, value: Optional = None):
        env_file = value or '.env'
        from dotenv import dotenv_values
        value = dotenv_values(env_file)
        return cls.register(value=value,provide=CONFIG_MODULE_TOKEN)
