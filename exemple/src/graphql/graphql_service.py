from exemple.src.user import UserService
from pesty.common.decorator import Injectable, Inject


@Injectable()
class GraphqlService:
    user_service: UserService = Inject(UserService)

    def get_test(self):
        return "test"
