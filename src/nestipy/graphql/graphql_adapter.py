from abc import ABC, abstractmethod
from typing import Any, Callable, Type, Union

from .graphql_asgi import GraphqlAsgi
from .graphql_module import GraphqlOption


class GraphqlAdapter(ABC):
    _query_properties: list = []
    _mutation_properties: list = []
    _subscription_properties: list = []

    @abstractmethod
    def create_query_field_resolver(self, resolver: Callable) -> object:
        pass

    @abstractmethod
    def create_type_field_resolver(self, prop: dict, resolve: Callable) -> object:
        pass

    @abstractmethod
    def raise_exception(self, e: Exception):
        pass

    @abstractmethod
    def create_mutation_field_resolver(self, resolver: Callable) -> object:
        pass

    @abstractmethod
    def create_subscription_field_resolver(self, resolver: Callable) -> object:
        pass

    def add_query_property(self, property_name: str, resolver: Callable):
        self._query_properties.append(
            (property_name, self.create_query_field_resolver(resolver))
        )

    def add_mutation_property(self, property_name: str, resolver: Callable):
        self._mutation_properties.append(
            (property_name, self.create_mutation_field_resolver(resolver))
        )

    def add_subscription_property(self, property_name: str, resolver: Callable):
        self._subscription_properties.append(
            (property_name, self.create_subscription_field_resolver(resolver))
        )

    def create_query(self, name: str = "Query") -> Union[Type, None]:
        if len(self._query_properties) == 0:
            return None
        return type(name, (), {k: r for (k, r) in self._query_properties})

    def create_mutation(self, name: str = "Mutation") -> Union[Type, None]:
        if len(self._mutation_properties) == 0:
            return None
        return type(name, (), {k: r for (k, r) in self._mutation_properties})

    def create_subscription(self, name: str = "Subscription") -> Union[Type, None]:
        if len(self._subscription_properties) == 0:
            return None
        return type(name, (), {k: r for (k, r) in self._subscription_properties})

    @abstractmethod
    def create_schema(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def mutate_handler(
        self,
        original_handler: Callable,
        wrapper_handler: Callable,
        default_return_type: Any,
    ) -> Type:
        pass

    @abstractmethod
    def create_graphql_asgi_app(
        self, schema: Any, option: GraphqlOption
    ) -> GraphqlAsgi:
        pass
