import asyncio

from ..common.enum.platform import PlatFormType
from ..core.app_context import AppPestyContext


class AppPestyFactory:
    @staticmethod
    def create(cls, platform=PlatFormType.LITESTAR, **kwargs)-> AppPestyContext:
        return AppPestyContext(module=cls, platform=platform, **kwargs)

