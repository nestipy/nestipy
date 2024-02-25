from __future__ import annotations

import dataclasses
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Mapping,
    Optional,
    Sequence,
    Type,
    Union,
)

from strawberry import BasePermission
from strawberry.annotation import StrawberryAnnotation
from strawberry.field import StrawberryField, _RESOLVER_TYPE
from strawberry.types.fields.resolver import StrawberryResolver

from .resolver import FieldResolver

if TYPE_CHECKING:
    from typing_extensions import Literal

    from strawberry.extensions.field_extension import FieldExtension


def field(
        resolver: Optional[_RESOLVER_TYPE[Any]] = None,
        *,
        name: Optional[str] = None,
        is_subscription: bool = False,
        description: Optional[str] = None,
        permission_classes: Optional[List[Type[BasePermission]]] = None,
        deprecation_reason: Optional[str] = None,
        default: Any = dataclasses.MISSING,
        default_factory: Union[Callable[..., object], object] = dataclasses.MISSING,
        metadata: Optional[Mapping[Any, Any]] = None,
        directives: Optional[Sequence[object]] = (),
        extensions: Optional[List[FieldExtension]] = None,
        graphql_type: Optional[Any] = None,
        init: Literal[True, False, None] = None,
) -> Any:
    type_annotation = StrawberryAnnotation.from_annotation(graphql_type)

    field_ = StrawberryField(
        python_name=None,
        graphql_name=name,
        type_annotation=type_annotation,
        description=description,
        is_subscription=is_subscription,
        permission_classes=permission_classes or [],
        deprecation_reason=deprecation_reason,
        default=default,
        default_factory=default_factory,
        metadata=metadata,
        directives=directives or (),
        extensions=extensions or [],
    )

    if resolver:
        assert init is not True, "Can't set init as True when passing a resolver."
        if not isinstance(resolver, StrawberryResolver):
            resolver = FieldResolver(resolver)
        return field_(resolver)
    return field_
