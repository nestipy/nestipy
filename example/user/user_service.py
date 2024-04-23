from nestipy_decorator import Injectable
from nestipy_ioc import Inject


@Injectable()
class UserService:
    tes: Inject['TEST']
