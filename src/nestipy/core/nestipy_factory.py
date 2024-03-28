from typing import Type

from .adapter.fastapi_adapter import FastApiAdapter
from .nestipy_application import NestipyApplication, NestipyApplicationConfig


class NestipyFactoryMeta(type):
    def __getitem__(self, item):
        setattr(self, '__generic_type__', item.__name__)
        return self


class NestipyFastApiApplication:
    pass


class NestipyBlackSheepApplication:
    pass


class NestipyFactory(metaclass=NestipyFactoryMeta):

    @classmethod
    def create(cls, module: Type, config: NestipyApplicationConfig = None) -> NestipyApplication:
        if hasattr(cls, '__generic_type__') and getattr(cls, '__generic_type__') == 'NestipyFastApiApplication':
            if not config:
                config = NestipyApplicationConfig(adapter=FastApiAdapter())
        application = NestipyApplication(config=config)
        application.init(module)
        return application

    @classmethod
    def create_micro_service(cls):
        pass
