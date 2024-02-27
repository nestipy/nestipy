from ...common.decorator.module import Module
from .constant import DATABASE_MODULE_TOKEN
from .database_service import DatabaseService
from ..dynamic_module.dynamic_module import DynamicModule
from ...core.module.provider import ModuleProvider


@Module(providers=[DatabaseService], exports=[DatabaseService], is_global=True)
class DatabaseModule(DynamicModule):

    @classmethod
    def for_root_async(cls, value: ModuleProvider, inject=None):
        return cls.register_async(
            provider=ModuleProvider(
                use_value=value,
                provide=DATABASE_MODULE_TOKEN,
                inject=inject or []
            )
        )
