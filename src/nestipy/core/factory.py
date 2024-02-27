import asyncio
import inspect
from typing import TypeVar, Generic

from ..common.enum.platform import PlatFormType
from ..core.app_context import AppNestipyContext
from ..core.platform import PlatformLitestar, PlatformAdapter

T = TypeVar('T', PlatformLitestar, PlatformAdapter, covariant=True)


class NestipyFactoryMeta(type):
    def __getitem__(self, item):
        setattr(self, '__generic_type__', item.__name__)
        return self


class NestipyFactory(metaclass=NestipyFactoryMeta):

    @classmethod
    def create(cls, module, **kwargs) -> AppNestipyContext:
        platform = PlatFormType.LITESTAR
        if hasattr(cls, '__generic_type__') and getattr(cls, '__generic_type__') == 'PlatformFastAPI':
            platform = PlatFormType.FASTAPI
        return AppNestipyContext(module=module, platform=platform, **kwargs)
