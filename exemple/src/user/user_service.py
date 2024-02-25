from pesty.common.decorator.inject import Inject
from pesty.common.decorator.injectable import Injectable
from pesty.plugins.config_module.config_service import ConfigService
from pesty.plugins.peewee_module.peewee_service import PeeweeService
from ..auth import AuthService
from .dto import CreateUserDto
from .entities.user import User
from .user_auth_service import UserAuthService


@Injectable()
class UserService:
    user_auth: UserAuthService = Inject(UserAuthService)
    auth_service: AuthService = Inject(AuthService)
    config: ConfigService = Inject(ConfigService)
    db: PeeweeService = Inject(PeeweeService)

    @classmethod
    def get_users(cls) -> list[dict]:
        return [u.to_json() for u in User.select()]

    @classmethod
    def create_user(cls, data: CreateUserDto) -> dict:
        p = User.create(name=data.name, city=data.city, age=data.age)
        return p.to_json()
