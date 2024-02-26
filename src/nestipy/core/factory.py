import asyncio

from ..common.enum.platform import PlatFormType
from ..core.app_context import AppNestipyContext


class AppNestipyFactory:
    @staticmethod
    def create(cls, platform=PlatFormType.LITESTAR, **kwargs)-> AppNestipyContext:
        return AppNestipyContext(module=cls, platform=platform, **kwargs)

