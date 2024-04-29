from abc import ABC

from .consumer import MiddlewareConsumer


class NestipyModule(ABC):
    def configure(self, consumer: MiddlewareConsumer):
        pass

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass
