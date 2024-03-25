from nestipy.common.decorator import Injectable
from nestipy.common.metadata.provider_token import ProviderToken
from nestipy.types_ import Inject


@Injectable()
class AppProvider:
    tes: Inject[ProviderToken('TEST')]
    pass
