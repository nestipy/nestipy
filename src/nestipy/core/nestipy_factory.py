import logging
import logging
import typing
from importlib import import_module
from typing import Type

from nestipy.common.logger import logger
from nestipy.microservice.client.base import MicroserviceOption
from .nestipy_application import NestipyApplication, NestipyConfig
from .nestipy_microservice import NestipyMicroservice, NestipyConnectMicroservice


class _NestipyFactoryMeta(type):
    def __getitem__(self, item) -> "NestipyFactory":
        setattr(self, "__generic_type__", item.__name__)
        return typing.cast(NestipyFactory, self)


class NestipyFactory(metaclass=_NestipyFactoryMeta):
    """
    Factory class for creating Nestipy application and microservice instances.
    """

    @classmethod
    def create(
        cls, module: Type, config: typing.Optional[NestipyConfig] = None
    ) -> NestipyApplication:
        """
        Create a Nestipy application.
        :param module: The root module of the application.
        :param config: Optional configuration for the application.
        :return: A NestipyApplication instance.
        """
        cls._setup_log()
        if getattr(cls, "__generic_type__", None) == "BlackSheepApplication":
            if not config:
                config = NestipyConfig(adapter=cls._load_adapter())
        application = NestipyApplication(config=config)
        application.init(module)
        return application

    @classmethod
    def create_microservice(
        cls, module: Type, option: list[MicroserviceOption]
    ) -> NestipyMicroservice:
        """
        Create a standalone Nestipy microservice.
        :param module: The root module of the microservice.
        :param option: List of microservice options (transport, host, port, etc).
        :return: A NestipyMicroservice instance.
        """
        return NestipyMicroservice(module, option)

    @classmethod
    def connect_microservice(
        cls,
        module: Type,
        option: list[MicroserviceOption],
        config: typing.Optional[NestipyConfig] = None,
    ) -> NestipyConnectMicroservice:
        """
        Connect a microservice to an existing Nestipy application.
        :param module: The root module for the microservice connection.
        :param option: List of microservice options.
        :param config: Optional configuration.
        :return: A NestipyConnectMicroservice instance.
        """
        return NestipyConnectMicroservice(module, config or NestipyConfig(), option)

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
            adapter_module = import_module("nestipy.core.adapter.blacksheep_adapter")
            logger.info("[Blacksheep Adapter] Using BlackSheepAdapter")
            return adapter_module.BlackSheepAdapter()
        except ImportError:
            try:
                # Fallback to FastAPI adapter
                adapter_module = import_module("nestipy.core.adapter.fastapi_adapter")
                logger.info("[FastAPI Adapter] Using FastAPIAdapter")
                return adapter_module.FastApiAdapter()
            except ImportError:
                raise RuntimeError(
                    "No suitable adapter found. Install extras with "
                    "`pip install nestipy[blacksheep]` or `pip install nestipy[fastapi]`."
                )
