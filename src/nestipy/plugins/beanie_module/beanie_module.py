import logging
import traceback
from typing import Callable, Awaitable

from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from nestipy.core.module.provider import ModuleProvider
from .constant import BEANIE_MODULE_CONFIG
from nestipy.plugins.dynamic_module.dynamic_module import DynamicModule
from nestipy.common.decorator import Module


@Module(is_global=True)
class BeanieModule(DynamicModule):
    documents = []

    @classmethod
    def for_feature(cls, models: list):
        beanie_documents = []
        for model in models:
            if issubclass(model, Document) and not hasattr(model, 'registered__'):
                beanie_documents.append(model)
                setattr(model, 'registered__', True)
        cls.documents = list(set(cls.documents + beanie_documents))
        return None

    @classmethod
    def for_root(cls, config: str = None, document: list = None):
        cls.for_feature(models=document or [])
        if config is not None:
            return cls.register(provide=BEANIE_MODULE_CONFIG, value=config)

    @classmethod
    def for_root_async(cls,
                       config: str = None,
                       use_factory: Callable[[...], Awaitable[str] | str] = None,
                       inject: list = None,
                       document: list = None
                       ):
        cls.documents += document or []
        if config is not None:
            return super().register(provide=BEANIE_MODULE_CONFIG, value=config)
        if use_factory is not None:
            return super().register_async(
                provider=ModuleProvider(
                    provide=BEANIE_MODULE_CONFIG,
                    use_factory=use_factory,
                    inject=inject or []
                )
            )

    async def on_startup(self):
        container_instance = self.get_container().instances
        if BEANIE_MODULE_CONFIG in container_instance.keys():
            config: str = container_instance[BEANIE_MODULE_CONFIG]
            client = AsyncIOMotorClient(config or "mongodb://user:password@host:27017")
            try:
                logging.info('Initializing mongo connection ...')
                await init_beanie(database=client.db_name, document_models=list(set(self.documents)))
                logging.info('Connection to mongo database successfully ...')
            except Exception as e:
                tb = traceback.format_exc()
                logging.error(e)
                logging.error(tb)
