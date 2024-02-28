import inspect
import json
import logging
import traceback
from dataclasses import dataclass, asdict
from typing import Any, Literal, Callable, Awaitable
from peewee import MySQLDatabase, PostgresqlDatabase, SqliteDatabase, Database, Model as BaseModel

from .constant import PEEWEE_MODULE_CONFIG
from .peewee_service import PeeweeService
from ..dynamic_module.dynamic_module import DynamicModule
from ...common.decorator.module import Module
from ...core.module.provider import ModuleProvider


@dataclass
class PeeweeDatabaseConfig:
    driver: Literal['mysql', 'postgres', 'sqlite']
    database: str
    host: str
    port: int
    user: str
    password: str


@Module(providers=[PeeweeService], exports=[PeeweeService], is_global=True)
class PeeweeModule(DynamicModule):
    models = []
    db: Database

    async def on_startup(self):
        container_instance = self.get_container().instances
        if PEEWEE_MODULE_CONFIG in container_instance.keys():
            config: PeeweeDatabaseConfig = container_instance[PEEWEE_MODULE_CONFIG]
            self.create_db(config)
            models = []
            for m in self.models:
                new_m = PeeweeModule.class_to_model(m, self.db)
                models.append(new_m)
            if not self.db.is_closed():
                self.db.close()
            self.db.connect()
            self.db.create_tables(self.models)

    async def on_shutdown(self):
        if self.db is not None:
            if not self.db.is_closed():
                self.db.close()

    def create_db(self, config: PeeweeDatabaseConfig):
        config_dict = asdict(config)
        del config_dict['driver']
        database = config_dict['database']
        del config_dict['database']
        match config.driver:
            case 'postgres':
                self.db = PostgresqlDatabase(database, **config_dict)
            case 'sqlite':
                self.db = SqliteDatabase(database, **config_dict)
            case _:
                self.db = MySQLDatabase(database, **config_dict)

    @classmethod
    def for_root_async(cls,
                       value: PeeweeDatabaseConfig = None,
                       use_factory: Callable[[...], Awaitable[PeeweeDatabaseConfig] | PeeweeDatabaseConfig] = None,
                       inject: list = None
                       ):
        return super().register_async(
            provider=ModuleProvider(
                use_value=value,
                provide=PEEWEE_MODULE_CONFIG,
                use_factory=use_factory,
                inject=inject or [])
        )

    @classmethod
    def for_feature(cls, models: list):
        peewee_models = []
        for model in models:
            if hasattr(model, 'peewee_model__'):
                peewee_models.append(model)
        cls.models = cls.models + peewee_models
        return None

    @staticmethod
    def to_json(self):
        r = {}
        members = inspect.getmembers(self,
                                     predicate=lambda a: not inspect.ismethod(a) and not inspect.isfunction(a))
        excludes = ['DoesNotExist', 'dirty_fields']
        filtered_members = [me for me in members if
                            not me[0].startswith('_') and not me[0].endswith('__') and me[0] not in excludes]
        for k, v in filtered_members:
            try:
                r[k] = v
            except Exception as e:
                tb = traceback.format_exc()
                logging.error(e)
                logging.error(tb)
                r[k] = json.dumps(getattr(self, k))
        return r

    @staticmethod
    def class_to_model(m, db):
        class_attrs = {"__module__": m.__module__, 'to_json': PeeweeModule.to_json}
        for name, value in inspect.getmembers(m):
            if not name.startswith('__'):
                class_attrs[name] = value
        meta = type('Meta', (), {'database': db, 'table_name': str(m.__name__).lower()})
        setattr(m, "Meta", meta)
        class_attrs['Meta'] = meta
        new_cls = type(m.__name__, (BaseModel,) + m.__bases__, class_attrs)
        new_class_member = inspect.getmembers(new_cls)
        for name, value in new_class_member:
            if not name.startswith('__'):
                setattr(m, name, value)

        globals()[m.__name__] = new_cls
        return new_cls
