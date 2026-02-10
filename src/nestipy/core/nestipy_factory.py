import logging
import typing
from importlib import import_module
from typing import Type

from nestipy.common.logger import logger, configure_logger, DEFAULT_LOG_FORMAT
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
        cls._setup_log(config)
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
        cls._setup_log(None)
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
        cls._setup_log(config)
        return NestipyConnectMicroservice(module, config or NestipyConfig(), option)

    @classmethod
    def _setup_log(cls, config: typing.Optional[NestipyConfig]):
        if config is None:
            configure_logger(level=logging.INFO)
            return
        def _resolve_level(value: typing.Optional[typing.Union[int, str]], default: int) -> int:
            if value is None:
                return default
            if isinstance(value, int):
                return value
            return logging._nameToLevel.get(value.upper(), default)

        level = _resolve_level(config.log_level, logging.INFO)
        file_level = _resolve_level(config.log_file_level, level)
        configure_logger(
            level=level,
            fmt=config.log_format or DEFAULT_LOG_FORMAT,
            datefmt=config.log_datefmt,
            use_color=config.log_color,
            file=config.log_file,
            file_level=file_level,
            attach_granian=True,
            force=True,
        )

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
