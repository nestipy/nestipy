from __future__ import annotations

from typing import Any, Protocol, TypedDict, NotRequired, Required, TypeVar, Generic, Callable

T = TypeVar("T")

class ActionError(Protocol):
    message: str
    type: str

class ActionResponse(Protocol, Generic[T]):
    ok: bool
    data: T | None
    error: ActionError | None

class JsPromise(Protocol, Generic[T]):
    def then(
        self,
        on_fulfilled: Callable[[T], Any] | None = ...,
        on_rejected: Callable[[Any], Any] | None = ...,
    ) -> "JsPromise[Any]": ...

class AppActionsHelloParams(TypedDict, total=False):
    name: NotRequired[str]

class AppActions(Protocol):
    def hello(self, params: AppActionsHelloParams) -> JsPromise[ActionResponse[str]]: ...

class ActionsClient(Protocol):
    AppActions: AppActions
    call: Callable[..., JsPromise[ActionResponse[Any]]]
