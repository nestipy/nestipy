from nestipy.common.decorator.middleware import Middleware, NestipyMiddleware
from litestar import Request
from litestar import Response


class UserMiddleware(NestipyMiddleware):

    def use(self, scope, receive, send):
        print('UserMiddleware called')


def create_middleware(scope, receive, send):
    print('create_middleware called ')
