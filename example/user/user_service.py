from nestipy_ioc import Inject

from nestipy.common import Injectable


@Injectable()
class UserService:
    tes: Inject['TEST']
