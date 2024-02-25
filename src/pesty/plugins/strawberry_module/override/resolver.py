from typing import Any, Generic
from typing import TypeVar

from strawberry.types.fields.resolver import StrawberryResolver

T = TypeVar('T')


class FieldResolver(Generic[T], StrawberryResolver[T]):
    def __call__(self, *args: str, **kwargs: Any) -> T:
        if not callable(self.wrapped_func):
            raise Exception(
                f"Attempted to call resolver {self.wrapped_func} with not callable function "
                f"{self.wrapped_func}"
            )
        if len(args) > 0 and hasattr(self.wrapped_func, 'metadata__'):
            args = (getattr(self.wrapped_func, 'metadata__'),)
        return self.wrapped_func(*args, **kwargs)
