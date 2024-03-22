from typing import Type

from .nestipy_application import NestipyApplication, NestipyApplicationConfig


class NestipyFactory:

    @classmethod
    def create(cls, module: Type, config: NestipyApplicationConfig = None) -> NestipyApplication:
        application = NestipyApplication(config=config)
        application.init(module)
        return application

    @classmethod
    def create_micro_service(cls):
        pass
