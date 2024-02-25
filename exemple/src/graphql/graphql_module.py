from exemple.src.graphql.graphql_resolver import GraphqlResolver
from pesty.common.decorator import Module


@Module(providers=[GraphqlResolver])
class GraphqlModule:
    pass
