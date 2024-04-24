from nestipy_ioc import Inject

from nestipy.common import Injectable


@Injectable()
class AppProvider:
    tes: Inject['TEST']
    pass
