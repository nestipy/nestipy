from __future__ import annotations

from typing import Any, Protocol, TypedDict, NotRequired, Required, TypeVar, Generic, Callable

T = TypeVar("T")

class JsPromise(Protocol, Generic[T]):
    def then(
        self,
        on_fulfilled: Callable[[T], Any] | None = ...,
        on_rejected: Callable[[Any], Any] | None = ...,
    ) -> "JsPromise[Any]": ...

class AppControllerMessageOptions(TypedDict, total=False):
    pass

class AppControllerPingOptions(TypedDict, total=False):
    pass

class ActionsControllerCsrfOptions(TypedDict, total=False):
    pass

ActionsControllerHandleBody = dict

class ActionsControllerHandleOptions(TypedDict, total=False):
    body: ActionsControllerHandleBody

class ActionsControllerSchemaOptions(TypedDict, total=False):
    pass

class AppControllerApi(Protocol):
    def message(self, options: AppControllerMessageOptions | None = None) -> JsPromise[str]: ...
    def ping(self, options: AppControllerPingOptions | None = None) -> JsPromise[str]: ...

class ActionsControllerApi(Protocol):
    def csrf(self, options: ActionsControllerCsrfOptions | None = None) -> JsPromise[dict[str, Any]]: ...
    def handle(self, options: ActionsControllerHandleOptions | None = None) -> JsPromise[dict[str, Any]]: ...
    def schema(self, options: ActionsControllerSchemaOptions | None = None) -> JsPromise[dict[str, Any]]: ...

class ApiClient(Protocol):
    AppController: AppControllerApi
    ActionsController: ActionsControllerApi
    App: AppControllerApi
    Actions: ActionsControllerApi
