from nestipy.common.decorator.injectable import Injectable
from nestipy.common.decorator.middleware import NestipyMiddleware


@Injectable()
class AppMiddleware(NestipyMiddleware):
    def use(self, scope, receive, send):
        print('Called')
