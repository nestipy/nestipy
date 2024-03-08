from ..auth.auth_module import AuthModule
from .graphql_resolver import GraphqlResolver
from .graphql_service import GraphqlService
from ..guard.guard_module import GuardModule
from ..user.user_module import UserModule
from nestipy.common.decorator import Module


@Module(
    providers=[
        GraphqlService,
        GraphqlResolver
    ],
    imports=[
        AuthModule,
        UserModule,
        GuardModule
    ]
)
class GraphqlModule:
    pass
