import typing
from typing import Type

from .adapter.blacksheep_adapter import BlackSheepAdapter
from .nestipy_application import NestipyApplication, NestipyApplicationConfig


class _NestipyFactoryMeta(type):
    def __getitem__(self, item) -> "NestipyFactory":
        setattr(self, '__generic_type__', item.__name__)
        return typing.cast(NestipyFactory, self)


class NestipyFactory(metaclass=_NestipyFactoryMeta):

    @classmethod
    def create(cls, module: Type, config: NestipyApplicationConfig = None) -> NestipyApplication:
        if getattr(cls, '__generic_type__', None) == 'NestipyBlackSheepApplication':
            if not config:
                config = NestipyApplicationConfig(adapter=BlackSheepAdapter())
        application = NestipyApplication(config=config)
        application.init(module)
        return application

    @classmethod
    def create_micro_service(cls):
        pass
