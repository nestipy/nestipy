from pesty.core.module.middleware import MiddlewareConsumer


class PestyModule:
    pesty_module__ = True

    def configure(self, consumer: MiddlewareConsumer):
        pass
