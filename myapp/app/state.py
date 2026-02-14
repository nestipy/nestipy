from __future__ import annotations

from typing import Callable, Literal, Protocol, TypedDict, TypeVar

from nestipy.web import create_context, external_fn

ThemeName = Literal["light", "dark"]


class ThemeContextValue(TypedDict):
    theme: ThemeName
    toggle: Callable[[], None] | None


class AppState(TypedDict):
    theme: ThemeName
    sharedCount: int
    toggleTheme: Callable[[], None]
    incShared: Callable[[], None]
    decShared: Callable[[], None]


T = TypeVar("T")


class UseAppStore(Protocol):
    def __call__(self, selector: Callable[[AppState], T]) -> T: ...


use_app_store: UseAppStore = external_fn("@/store", "useAppStore", alias="useAppStore")

theme_default: ThemeContextValue = {"theme": "dark", "toggle": None}
ThemeContext = create_context(theme_default)