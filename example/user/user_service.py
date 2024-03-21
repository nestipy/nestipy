from nestipy.common.decorator import Injectable
from nestipy.common.metadata.provide import Provide
from nestipy.types_.dependency import Inject


@Injectable()
class UserService:
    tes: Inject[Provide('TEST')]
