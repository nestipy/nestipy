from nestipy.ioc import Inject

from nestipy.common import Injectable
from nestipy.core import OnInit


@Injectable()
class UserService(OnInit):
    tes: Inject['TEST']

    async def on_startup(self):
        print('On init service')

    async def on_shutdown(self):
        pass
