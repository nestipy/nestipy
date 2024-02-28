from dataclasses import dataclass, asdict
from typing import Optional, Callable, Awaitable

from masoniteorm.connections import ConnectionResolver

from nestipy.common import Module
from nestipy.core.module import NestipyModule
from nestipy.core.module.provider import ModuleProvider
from nestipy.plugins.dynamic_module.dynamic_module import DynamicModule

MASONITE_ORM_DB = 'MASONITE_ORM_DB'
MASONITE_ORM_CONFIG = 'MASONITE_ORM_CONFIG'


@dataclass
class MasoniteDatabaseConfig:
    driver: str
    host: str
    port: str
    user: str
    password: str
    database: str
    prefix: str = ''
    log_queries: bool = False


ConfigType = dict[str, MasoniteDatabaseConfig | str]


@Module(is_global=True)
class MasoniteOrmModule(DynamicModule, NestipyModule):
    @classmethod
    def for_root(cls, config: ConfigType):
        DB = ConnectionResolver()
        setattr(cls, 'DATABASES', config)
        setattr(cls, 'DB', DB)
        cls.register(provide=MASONITE_ORM_DB, value=DB)

    @classmethod
    def for_root_async(cls,
                       value: Optional[ConfigType] = None,
                       factory: Callable[..., Awaitable[ConfigType] | ConfigType] = None,
                       inject: list = None
                       ):
        if value is not None:
            DB = ConnectionResolver()
            setattr(cls, 'DATABASES', value)
            setattr(cls, 'DB', DB)
            return cls.register(provide=MASONITE_ORM_DB, value=DB)
        if factory is not None:
            return cls.register_async(
                provider=ModuleProvider(
                    provide=MASONITE_ORM_CONFIG,
                    use_factory=factory, inject=inject or []
                )
            )

    def on_startup(self):
        instances: dict = self.get_container().instances
        if MASONITE_ORM_CONFIG in instances.keys():
            config = MasoniteOrmModule.to_dict(instances[MASONITE_ORM_CONFIG])
            DB = ConnectionResolver().set_connection_details(config)
            setattr(self, 'DB', DB)
        else:
            DB: ConnectionResolver = getattr(self, 'DB', ConnectionResolver())
            DATABASES = getattr(self, 'DATABASES', {})
            DB.set_connection_details(MasoniteOrmModule.to_dict(DATABASES))
            setattr(self, 'DB', DB)

    @classmethod
    def get_db(cls):
        return getattr(cls, 'DB', None)

    @classmethod
    def to_dict(cls, config: dict[str, MasoniteDatabaseConfig]):
        config_dict = {}
        for key, value in config.items():
            config_dict[key] = asdict(value) if not isinstance(value, str) else value
        return config_dict
