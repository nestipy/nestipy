from pesty.common.decorator.injectable import Injectable
from pesty.common.decorator.middleware import PestyMiddleware


@Injectable()
class AppMiddleware(PestyMiddleware):
    def use(self, scope, receive, send):
        pass
