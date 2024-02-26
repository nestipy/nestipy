from ...common.decorator.module import Module
from .constant import DATABASE_MODULE_TOKEN
from .database_service import DatabaseService
from ..dynamic_module.dynamic_module import DynamicModule, ModuleOption


@Module(providers=[DatabaseService], exports=[DatabaseService], is_global=True)
class DatabaseModule(DynamicModule):

    @classmethod
    def for_root_async(cls, value: ModuleOption, inject=None):
        if inject is None:
            inject = []
        return cls.register_async(value, DATABASE_MODULE_TOKEN, inject)

