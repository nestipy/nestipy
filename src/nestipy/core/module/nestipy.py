from nestipy.core.module.middleware import MiddlewareConsumer


class NestipyModule:
    nestipy_module__ = True

    def configure(self, consumer: MiddlewareConsumer):
        pass

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass
