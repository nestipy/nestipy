from exemple.src.graphql.graphql_resolver import GraphqlResolver
from exemple.src.graphql.graphql_service import GraphqlService
from exemple.src.user.user_module import UserModule
from nestipy.common.decorator import Module


@Module(providers=[GraphqlService, GraphqlResolver], imports=[UserModule])
class GraphqlModule:
    pass
