import logging
import typing
from importlib import import_module
from typing import Type

from .nestipy_application import NestipyApplication, NestipyConfig

from nestipy.microservice.client.base import MicroserviceOption
from .nestipy_microservice import NestipyMicroservice, NestipyConnectMicroservice


class _NestipyFactoryMeta(type):
    def __getitem__(self, item) -> "NestipyFactory":
        setattr(self, "__generic_type__", item.__name__)
        return typing.cast(NestipyFactory, self)


class NestipyFactory(metaclass=_NestipyFactoryMeta):
    @classmethod
    def create(
            cls, module: Type, config: typing.Optional[NestipyConfig] = None
    ) -> NestipyApplication:
        cls._setup_log()
        if getattr(cls, "__generic_type__", None) == "NestipyBlackSheepApplication":
            if not config:
                config = NestipyConfig(adapter=cls._load_adapter())
        application = NestipyApplication(config=config)
        application.init(module)
        return application

    @classmethod
    def create_microservice(
            cls, module: Type, option: list[MicroserviceOption]
    ) -> NestipyMicroservice:
        return NestipyMicroservice(module, option)

    @classmethod
    def connect_microservice(
            cls,
            module: Type,
            option: list[MicroserviceOption],
            config: typing.Optional[NestipyConfig] = None,
    ) -> NestipyConnectMicroservice:
        return NestipyConnectMicroservice(module, config, option)

    @classmethod
    def _setup_log(cls):
        logging.addLevelName(logging.INFO, "[NESTIPY] INFO")
        logging.addLevelName(logging.ERROR, "[NESTIPY] ERROR")
        logging.addLevelName(logging.WARNING, "[NESTIPY] WARNING")
        logging.addLevelName(logging.WARN, "[NESTIPY] WARN")
        logging.addLevelName(logging.CRITICAL, "[NESTIPY] CRITICAL")

    @classmethod
    def _load_adapter(cls):
        """
        Dynamically load the appropriate adapter (BlackSheep or FastAPI).
        """
        try:
            # Try to load the BlackSheep adapter
            adapter_module = import_module("nestipy.adapters.blacksheep_adapter")
            return adapter_module.BlackSheepAdapter()
        except ImportError:
            try:
                # Fallback to FastAPI adapter
                adapter_module = import_module("nestipy.adapters.fastapi_adapter")
                return adapter_module.FastAPIAdapter()
            except ImportError:
                raise RuntimeError(
                    "No suitable adapter found. Install extras with "
                    "`pip install nestipy[blacksheep]` or `pip install nestipy[fastapi]`."
                )
