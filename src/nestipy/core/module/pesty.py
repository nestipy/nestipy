from nestipy.core.module.middleware import MiddlewareConsumer


class NestipyModule:
    nestipy_module__ = True

    def configure(self, consumer: MiddlewareConsumer):
        pass
