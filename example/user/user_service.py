from nestipy.common.decorator import Injectable
from nestipy.common.metadata.provider_token import ProviderToken
from nestipy.types_.dependency import Inject


@Injectable()
class UserService:
    tes: Inject[ProviderToken('TEST')]
