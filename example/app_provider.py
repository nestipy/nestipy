from nestipy_decorator import Injectable
from nestipy_ioc import Inject


@Injectable()
class AppProvider:
    tes: Inject['TEST']
    pass
