from typing import Type

from .nestipy_application import NestipyApplication


class NestipyFactory:

    @classmethod
    def create(cls, module: Type) -> NestipyApplication:
        application = NestipyApplication()
        application.init(module)
        return application

    @classmethod
    def create_micro_service(cls):
        pass
