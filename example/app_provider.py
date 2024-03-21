from nestipy.common.decorator import Injectable
from nestipy.common.metadata.provide import Provide
from nestipy.types_ import Inject


@Injectable()
class AppProvider:
    tes: Inject[Provide('TEST')]
    pass
