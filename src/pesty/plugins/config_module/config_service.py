from ...common.decorator.inject import Inject
from ...common.decorator.injectable import Injectable
from .constant import CONFIG_MODULE_TOKEN


@Injectable()
class ConfigService:
    env: dict = Inject(CONFIG_MODULE_TOKEN)

    def get(self, key, default=None) -> str:
        return self.env.get(key) or default
