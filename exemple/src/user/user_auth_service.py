from nestipy.common.decorator.inject import Inject
from nestipy.common.decorator.injectable import Injectable
from ..auth import AuthService
from ..user.entities.user import User


@Injectable()
class UserAuthService:
    auth_s: AuthService = Inject(AuthService)

    def get_text(self):
        user = User.create(name='username', city='name', age=18)
        user.save()
        return "user auth ::: " + self.auth_s.get_user() + "DATA ::: " + user.name+' --- '
