from pesty.common.decorator.injectable import Injectable


@Injectable()
class AuthService:

    def get_user(self) -> str:
        return "User"
