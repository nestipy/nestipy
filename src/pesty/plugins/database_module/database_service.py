from ...common.decorator.inject import Inject
from ...common.decorator.injectable import Injectable
from .constant import DATABASE_MODULE_TOKEN


@Injectable()
class DatabaseService:
    url: str = Inject(DATABASE_MODULE_TOKEN)

    def get_url(self, ) -> str:
        return self.url
