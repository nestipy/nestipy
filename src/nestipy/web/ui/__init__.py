from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Protocol, TypedDict, TypeVar, Generic

COMPONENT_MARK_ATTR = "__nestipy_web_component__"
COMPONENT_NAME_ATTR = "__nestipy_web_component_name__"
PROPS_MARK_ATTR = "__nestipy_web_props__"


class HTMLProps(TypedDict, total=False):
    """Typed HTML/SVG props accepted by the `h` helper."""
    id: str
    key: str
    class_name: str
    class_: str
    data_: dict[str, Any]
    aria_: dict[str, Any]
    title: str
    style: str | dict[str, Any]
    role: str
    tab_index: int
    hidden: bool
    disabled: bool
    checked: bool
    selected: bool
    read_only: bool
    multiple: bool
    required: bool
    value: Any
    name: str
    type: str
    placeholder: str
    href: str
    target: str
    rel: str
    src: str
    alt: str
    width: int | str
    height: int | str
    rows: int
    cols: int
    col_span: int
    row_span: int
    min: int | float | str
    max: int | float | str
    min_length: int
    max_length: int
    pattern: str
    step: int | float | str
    for_: str
    http_equiv: str
    accept_charset: str
    accept: str
    capture: str
    content: str
    method: str
    action: str
    enc_type: str
    no_validate: bool
    form: str
    list: str
    size: int
    wrap: str
    auto_complete: str
    auto_focus: bool
    download: str | bool
    draggable: bool
    spell_check: bool
    content_editable: bool
    on_click: Any
    on_change: Any
    on_input: Any
    on_submit: Any
    on_key_down: Any
    on_key_up: Any
    on_key_press: Any
    on_mouse_enter: Any
    on_mouse_leave: Any
    on_mouse_over: Any
    on_mouse_out: Any
    on_focus: Any
    on_blur: Any
    on_scroll: Any
    on_load: Any
    on_error: Any
    on_double_click: Any
    on_mouse_down: Any
    on_mouse_up: Any
    on_mouse_move: Any
    on_mouse_wheel: Any
    on_context_menu: Any
    on_drag: Any
    on_drag_start: Any
    on_drag_end: Any
    on_drag_over: Any
    on_drag_enter: Any
    on_drag_leave: Any
    on_drop: Any
    on_touch_start: Any
    on_touch_end: Any
    on_touch_move: Any
    on_touch_cancel: Any
    on_pointer_down: Any
    on_pointer_up: Any
    on_pointer_move: Any
    on_pointer_enter: Any
    on_pointer_leave: Any
    on_pointer_over: Any
    on_pointer_out: Any
    on_copy: Any
    on_cut: Any
    on_paste: Any
    on_focus_in: Any
    on_focus_out: Any
    on_wheel: Any
    on_animation_start: Any
    on_animation_end: Any
    on_animation_iteration: Any
    on_transition_end: Any
    on_submit_capture: Any
    on_change_capture: Any
    on_key_down_capture: Any
    on_key_up_capture: Any
    on_key_press_capture: Any
    on_mouse_enter_capture: Any
    on_mouse_leave_capture: Any
    on_focus_capture: Any
    on_blur_capture: Any
    on_load_capture: Any
    on_error_capture: Any
    on_input_capture: Any
    on_wheel_capture: Any

    # SVG props
    fill: str
    stroke: str
    stroke_width: int | float | str
    stroke_linecap: str
    stroke_linejoin: str
    stroke_dasharray: str
    stroke_dashoffset: str
    stroke_miterlimit: int | float | str
    stroke_opacity: float | str
    fill_opacity: float | str
    opacity: float | str
    view_box: str
    preserve_aspect_ratio: str
    d: str
    cx: int | float | str
    cy: int | float | str
    r: int | float | str
    rx: int | float | str
    ry: int | float | str
    x: int | float | str
    y: int | float | str
    x1: int | float | str
    x2: int | float | str
    y1: int | float | str
    y2: int | float | str
    points: str
    path_length: int | float | str
    transform: str
    href_xlink: str
    clip_path: str
    mask: str
    filter: str
    xmlns: str
    xmlns_xlink: str
    gradient_units: str
    gradient_transform: str
    spread_method: str
    offset: str
    stop_color: str
    stop_opacity: float | str
    marker_start: str
    marker_mid: str
    marker_end: str
    dominant_baseline: str
    text_anchor: str
    alignment_baseline: str


@dataclass(frozen=True, slots=True)
class ExternalComponent:
    """Reference to a component imported from an external module."""
    module: str
    name: str
    default: bool = False
    alias: str | None = None

    @property
    def import_name(self) -> str:
        """Return the name to use in import statements."""
        return self.alias or self.name

    def __call__(self, *children: Child, **props: HTMLProps) -> "Node":
        """Create a Node that references this external component."""
        return Node(tag=self, props=_normalize_props(props), children=_flatten_children(children))


@dataclass(frozen=True, slots=True)
class ExternalFunction:
    """Reference to a callable imported from an external module."""
    module: str
    name: str
    alias: str | None = None

    @property
    def import_name(self) -> str:
        """Return the name to use in import statements."""
        return self.alias or self.name

    def __call__(self, *args: Any, **kwargs: Any) -> object:
        """Disallow runtime execution (compile-time only)."""
        raise RuntimeError("external_fn is compile-time only and cannot run at runtime.")


@dataclass(slots=True)
class Node:
    """Render tree node that represents a JSX element."""
    tag: Any
    props: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


class JSExpr(str):
    """Raw JS expression marker for props."""


@dataclass(frozen=True, slots=True)
class ConditionalExpr:
    """Represent a conditional JSX expression."""
    test: JSExpr
    consequent: Any
    alternate: Any


@dataclass(frozen=True, slots=True)
class ForExpr:
    """Represent a list comprehension compiled to JS map/filter."""
    target: str
    iterable: JSExpr
    body: Any
    condition: JSExpr | None = None


@dataclass(frozen=True, slots=True)
class LocalComponent:
    """Reference to a local component defined in the app."""
    name: str

    def __call__(self, *children: Child, **props: HTMLProps) -> "Node":
        """Create a Node that references this local component."""
        return Node(tag=self, props=_normalize_props(props), children=_flatten_children(children))


class _Fragment:
    """Marker type for fragment rendering."""
    pass


class _Slot:
    """Marker type for layout slot rendering."""
    pass


Fragment = _Fragment()
Slot = _Slot()

TContext = TypeVar("TContext")
TState = TypeVar("TState")
TValue = TypeVar("TValue")


class Context(Generic[TContext]):
    """Lightweight placeholder for React contexts (compile-time only)."""

    Provider: Any = object()
    Consumer: Any = object()

    def __init__(self, default: TContext | None = None) -> None:
        self.default = default


class StoreSelector(Protocol[TState, TValue]):
    """Typed selector for client-side stores (compile-time only)."""

    def __call__(self, state: TState) -> TValue: ...


class StoreHook(Protocol[TState]):
    """Typed store hook wrapper (compile-time only)."""

    def __call__(self, selector: StoreSelector[TState, TValue]) -> TValue: ...


Child = Node | str | int | float | bool | None | JSExpr


class TagCallable(Protocol):
    def __call__(self, *children: Child, **props: HTMLProps) -> "Node":
        """Render a Node for a concrete HTML tag."""
        ...


def js(expr: str) -> JSExpr:
    """Wrap a raw JavaScript expression for JSX output."""
    return JSExpr(expr)


def new_(constructor: Any, *args: Any) -> Any:
    """Declare a JavaScript `new` expression (compile-time only)."""
    raise RuntimeError("new_ is a compile-time helper and cannot run at runtime.")


def external(module: str, name: str, *, default: bool = False, alias: str | None = None) -> ExternalComponent:
    """Create a reference to an external component import."""
    return ExternalComponent(module=module, name=name, default=default, alias=alias)


def external_fn(module: str, name: str, *, alias: str | None = None) -> Type[ExternalFunction]:
    """Create a reference to an external function import."""
    return ExternalFunction(module=module, name=name, alias=alias)


def component(fn: Callable) -> Callable:
    """Mark a Python function as a component."""
    setattr(fn, COMPONENT_MARK_ATTR, True)
    setattr(fn, COMPONENT_NAME_ATTR, fn.__name__)
    return fn


def props(cls: type) -> type:
    """Mark a class as a props definition."""
    setattr(cls, PROPS_MARK_ATTR, True)
    return cls


def use_state(initial: Any = None) -> tuple[Any, Callable[[Any | Callable[[Any], Any]], None]]:
    """Declare a React useState hook (compile-time only)."""
    raise RuntimeError("use_state is a compile-time hook and cannot run at runtime.")


def use_effect(effect: Callable[[], None], deps: Any | None = None) -> None:
    """Declare a React useEffect hook (compile-time only)."""
    raise RuntimeError("use_effect is a compile-time hook and cannot run at runtime.")


def use_effect_async(effect: Callable[[], None], deps: Any | None = None) -> None:
    """Declare an async React useEffect hook (compile-time only)."""
    raise RuntimeError("use_effect_async is a compile-time hook and cannot run at runtime.")


def use_memo(factory: Callable[[], Any], deps: Any | None = None) -> Any:
    """Declare a React useMemo hook (compile-time only)."""
    raise RuntimeError("use_memo is a compile-time hook and cannot run at runtime.")


def use_callback(callback: Callable[..., Any], deps: list[Any] | None = None) -> Callable[..., Any]:
    """Declare a React useCallback hook (compile-time only)."""
    raise RuntimeError("use_callback is a compile-time hook and cannot run at runtime.")


def use_context(context: Context[TContext]) -> TContext:
    """Declare a React useContext hook (compile-time only)."""
    raise RuntimeError("use_context is a compile-time hook and cannot run at runtime.")


def use_ref(initial: Any = None) -> Any:
    """Declare a React useRef hook (compile-time only)."""
    raise RuntimeError("use_ref is a compile-time hook and cannot run at runtime.")


def create_context(default: TContext | None = None) -> Context[TContext]:
    """Declare a React context at module scope (compile-time only)."""
    raise RuntimeError("create_context is a compile-time helper and cannot run at runtime.")


def _flatten_children(children: Iterable[Any]) -> list[Any]:
    """Flatten nested children lists into a single list."""
    out: list[Any] = []
    for child in children:
        if child is None:
            continue
        if isinstance(child, (list, tuple)):
            out.extend(_flatten_children(child))
        else:
            out.append(child)
    return out


class H:
    """Factory for building Node trees with attribute access for tags."""
    def __call__(
        self,
        tag: Any,
        props: dict[str, Any] | None = None,
        *children: Child,
        **kwargs: Any,
    ) -> Node:
        """Create a Node with a dynamic tag and props."""
        actual_props: dict[str, Any] = {}
        if isinstance(props, dict):
            actual_props.update(props)
        elif props is not None:
            children = (props,) + children
        if kwargs:
            actual_props.update(_normalize_props(kwargs))
        return Node(tag=tag, props=actual_props, children=_flatten_children(children))

    def __getattr__(self, tag: str) -> TagCallable:
        """Return a callable that builds a Node for the given tag."""
        def _tag(*children: Child, **kwargs: Any) -> Node:
            """Build a Node for a specific HTML/SVG tag."""
            props: dict[str, Any] = {}
            if children and isinstance(children[0], dict):
                props.update(children[0])
                children = children[1:]
            if kwargs:
                props.update(_normalize_props(kwargs))
            return Node(tag=tag, props=props, children=_flatten_children(children))

        return _tag


def _normalize_props(props: dict[str, Any]) -> dict[str, Any]:
    """Normalize prop keys and expand data_/aria_ maps."""
    normalized: dict[str, Any] = {}
    for key, value in props.items():
        if key in {"data_", "aria_"} and isinstance(value, dict):
            prefix = "data-" if key == "data_" else "aria-"
            for sub_key, sub_value in value.items():
                normalized[prefix + str(sub_key).replace("_", "-")] = sub_value
            continue
        normalized[_normalize_prop_key(key)] = value
    return normalized


def _normalize_prop_key(key: str) -> str:
    """Normalize Pythonic prop keys to JSX-friendly names."""
    if key in {"class_name", "class_"}:
        return "className"
    if key == "for_":
        return "htmlFor"
    if key == "http_equiv":
        return "httpEquiv"
    if key == "accept_charset":
        return "acceptCharset"
    if key.startswith("data_"):
        return "data-" + key[5:].replace("_", "-")
    if key.startswith("aria_"):
        return "aria-" + key[5:].replace("_", "-")
    if key.endswith("_"):
        key = key[:-1]
    if "_" in key:
        parts = key.split("_")
        return parts[0] + "".join(part.capitalize() for part in parts[1:])
    return key


h = H()


__all__ = [
    "Node",
    "ExternalComponent",
    "ExternalFunction",
    "JSExpr",
    "LocalComponent",
    "Fragment",
    "Slot",
    "Context",
    "HTMLProps",
    "Child",
    "TagCallable",
    "COMPONENT_MARK_ATTR",
    "COMPONENT_NAME_ATTR",
    "PROPS_MARK_ATTR",
    "js",
    "new_",
    "external",
    "external_fn",
    "props",
    "component",
    "h",
    "use_state",
    "use_effect",
    "use_effect_async",
    "use_memo",
    "use_callback",
    "use_context",
    "use_ref",
    "create_context",
]
