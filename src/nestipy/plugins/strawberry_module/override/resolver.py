from typing import Any, Generic, Union, Callable, Optional
from typing import TypeVar

from strawberry.type import StrawberryType
from strawberry.types.fields.resolver import StrawberryResolver

T = TypeVar('T')


class FieldResolver(Generic[T], StrawberryResolver[T]):

    def __init__(
            self,
            func: Union[Callable[..., T], staticmethod, classmethod],
            *,
            description: Optional[str] = None,
            type_override: Optional[Union[StrawberryType, type]] = None,
    ):
        self.wrapped_func = func
        self._description = description
        self._type_override = type_override
        """Specify the type manually instead of calculating from wrapped func

        This is used when creating copies of types w/ generics
        """
        super().__init__(func=func, description=description, type_override=type_override)

    def __call__(self, *args: str, **kwargs: Any) -> T:
        if not callable(self.wrapped_func):
            raise Exception(
                f"Attempted to call resolver {self.wrapped_func} with not callable function "
                f"{self.wrapped_func}"
            )
        if len(args) > 0 and hasattr(self.wrapped_func, 'metadata__'):
            args = (getattr(self.wrapped_func, 'metadata__'),)
        return self.wrapped_func(*args, **kwargs)
