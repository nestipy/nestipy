from pesty.common.decorator.middleware import Middleware, PestyMiddleware


class UserMiddleware(PestyMiddleware):

    def use(self, scope, receive, send):
        print('UserMiddleware called ')


def create_middleware(scope, receive, send):
    print('create_middleware called ')
