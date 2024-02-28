from ...common.decorator.inject import Inject
from ...common.decorator.injectable import Injectable
from .constant import PEEWEE_MODULE_CONFIG


@Injectable()
class PeeweeService:
    config: dict = Inject(PEEWEE_MODULE_CONFIG)

    def get_config(self, ) -> dict:
        return self.config
