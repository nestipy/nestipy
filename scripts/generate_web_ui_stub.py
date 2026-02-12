from __future__ import annotations

from pathlib import Path

HTML_TAGS = [
    "a",
    "abbr",
    "address",
    "area",
    "article",
    "aside",
    "audio",
    "b",
    "base",
    "bdi",
    "bdo",
    "blockquote",
    "body",
    "br",
    "button",
    "canvas",
    "caption",
    "cite",
    "code",
    "col",
    "colgroup",
    "data",
    "datalist",
    "dd",
    "del",
    "details",
    "dfn",
    "dialog",
    "div",
    "dl",
    "dt",
    "em",
    "embed",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hgroup",
    "hr",
    "html",
    "i",
    "iframe",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "link",
    "main",
    "map",
    "mark",
    "menu",
    "meta",
    "meter",
    "nav",
    "noscript",
    "object",
    "ol",
    "optgroup",
    "option",
    "output",
    "p",
    "param",
    "picture",
    "pre",
    "progress",
    "q",
    "rp",
    "rt",
    "ruby",
    "s",
    "samp",
    "script",
    "search",
    "section",
    "select",
    "slot",
    "small",
    "source",
    "span",
    "strong",
    "style",
    "sub",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "template",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "title",
    "tr",
    "track",
    "u",
    "ul",
    "var",
    "video",
    "wbr",
]

SVG_TAGS = [
    "svg",
    "g",
    "defs",
    "desc",
    "title",
    "symbol",
    "use",
    "image",
    "path",
    "rect",
    "circle",
    "ellipse",
    "line",
    "polyline",
    "polygon",
    "text",
    "tspan",
    "textPath",
    "marker",
    "pattern",
    "mask",
    "clipPath",
    "linearGradient",
    "radialGradient",
    "stop",
    "filter",
    "feBlend",
    "feColorMatrix",
    "feComponentTransfer",
    "feComposite",
    "feConvolveMatrix",
    "feDiffuseLighting",
    "feDisplacementMap",
    "feDistantLight",
    "feFlood",
    "feFuncA",
    "feFuncB",
    "feFuncG",
    "feFuncR",
    "feGaussianBlur",
    "feImage",
    "feMerge",
    "feMergeNode",
    "feMorphology",
    "feOffset",
    "fePointLight",
    "feSpecularLighting",
    "feSpotLight",
    "feTile",
    "feTurbulence",
    "foreignObject",
]

HTML_PROPS = [
    ("id", "str"),
    ("class_name", "str"),
    ("class_", "str"),
    ("data_", "dict[str, Any]"),
    ("aria_", "dict[str, Any]"),
    ("title", "str"),
    ("style", "str | dict[str, Any]"),
    ("role", "str"),
    ("tab_index", "int"),
    ("hidden", "bool"),
    ("disabled", "bool"),
    ("checked", "bool"),
    ("selected", "bool"),
    ("read_only", "bool"),
    ("multiple", "bool"),
    ("required", "bool"),
    ("value", "Any"),
    ("name", "str"),
    ("type", "str"),
    ("placeholder", "str"),
    ("href", "str"),
    ("target", "str"),
    ("rel", "str"),
    ("src", "str"),
    ("alt", "str"),
    ("width", "int | str"),
    ("height", "int | str"),
    ("rows", "int"),
    ("cols", "int"),
    ("col_span", "int"),
    ("row_span", "int"),
    ("min", "int | float | str"),
    ("max", "int | float | str"),
    ("min_length", "int"),
    ("max_length", "int"),
    ("pattern", "str"),
    ("step", "int | float | str"),
    ("for_", "str"),
    ("http_equiv", "str"),
    ("accept_charset", "str"),
    ("accept", "str"),
    ("capture", "str"),
    ("content", "str"),
    ("method", "str"),
    ("action", "str"),
    ("enc_type", "str"),
    ("no_validate", "bool"),
    ("form", "str"),
    ("list", "str"),
    ("size", "int"),
    ("wrap", "str"),
    ("auto_complete", "str"),
    ("auto_focus", "bool"),
    ("download", "str | bool"),
    ("draggable", "bool"),
    ("spell_check", "bool"),
    ("content_editable", "bool"),
    ("on_click", "Any"),
    ("on_change", "Any"),
    ("on_input", "Any"),
    ("on_submit", "Any"),
    ("on_key_down", "Any"),
    ("on_key_up", "Any"),
    ("on_key_press", "Any"),
    ("on_mouse_enter", "Any"),
    ("on_mouse_leave", "Any"),
    ("on_mouse_over", "Any"),
    ("on_mouse_out", "Any"),
    ("on_focus", "Any"),
    ("on_blur", "Any"),
    ("on_scroll", "Any"),
    ("on_load", "Any"),
    ("on_error", "Any"),
    ("on_double_click", "Any"),
    ("on_mouse_down", "Any"),
    ("on_mouse_up", "Any"),
    ("on_mouse_move", "Any"),
    ("on_mouse_wheel", "Any"),
    ("on_context_menu", "Any"),
    ("on_drag", "Any"),
    ("on_drag_start", "Any"),
    ("on_drag_end", "Any"),
    ("on_drag_over", "Any"),
    ("on_drag_enter", "Any"),
    ("on_drag_leave", "Any"),
    ("on_drop", "Any"),
    ("on_touch_start", "Any"),
    ("on_touch_end", "Any"),
    ("on_touch_move", "Any"),
    ("on_touch_cancel", "Any"),
    ("on_pointer_down", "Any"),
    ("on_pointer_up", "Any"),
    ("on_pointer_move", "Any"),
    ("on_pointer_enter", "Any"),
    ("on_pointer_leave", "Any"),
    ("on_pointer_over", "Any"),
    ("on_pointer_out", "Any"),
    ("on_copy", "Any"),
    ("on_cut", "Any"),
    ("on_paste", "Any"),
    ("on_focus_in", "Any"),
    ("on_focus_out", "Any"),
    ("on_wheel", "Any"),
    ("on_animation_start", "Any"),
    ("on_animation_end", "Any"),
    ("on_animation_iteration", "Any"),
    ("on_transition_end", "Any"),
    ("on_submit_capture", "Any"),
    ("on_change_capture", "Any"),
    ("on_key_down_capture", "Any"),
    ("on_key_up_capture", "Any"),
    ("on_key_press_capture", "Any"),
    ("on_mouse_enter_capture", "Any"),
    ("on_mouse_leave_capture", "Any"),
    ("on_focus_capture", "Any"),
    ("on_blur_capture", "Any"),
    ("on_load_capture", "Any"),
    ("on_error_capture", "Any"),
    ("on_input_capture", "Any"),
    ("on_wheel_capture", "Any"),

    # SVG props
    ("fill", "str"),
    ("stroke", "str"),
    ("stroke_width", "int | float | str"),
    ("stroke_linecap", "str"),
    ("stroke_linejoin", "str"),
    ("stroke_dasharray", "str"),
    ("stroke_dashoffset", "str"),
    ("stroke_miterlimit", "int | float | str"),
    ("stroke_opacity", "float | str"),
    ("fill_opacity", "float | str"),
    ("opacity", "float | str"),
    ("view_box", "str"),
    ("preserve_aspect_ratio", "str"),
    ("d", "str"),
    ("cx", "int | float | str"),
    ("cy", "int | float | str"),
    ("r", "int | float | str"),
    ("rx", "int | float | str"),
    ("ry", "int | float | str"),
    ("x", "int | float | str"),
    ("y", "int | float | str"),
    ("x1", "int | float | str"),
    ("x2", "int | float | str"),
    ("y1", "int | float | str"),
    ("y2", "int | float | str"),
    ("points", "str"),
    ("path_length", "int | float | str"),
    ("transform", "str"),
    ("href_xlink", "str"),
    ("clip_path", "str"),
    ("mask", "str"),
    ("filter", "str"),
    ("xmlns", "str"),
    ("xmlns_xlink", "str"),
    ("gradient_units", "str"),
    ("gradient_transform", "str"),
    ("spread_method", "str"),
    ("offset", "str"),
    ("stop_color", "str"),
    ("stop_opacity", "float | str"),
    ("marker_start", "str"),
    ("marker_mid", "str"),
    ("marker_end", "str"),
    ("dominant_baseline", "str"),
    ("text_anchor", "str"),
    ("alignment_baseline", "str"),
]


def render() -> str:
    lines: list[str] = []
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from typing import Any, Callable, Iterable, Protocol, TypedDict, TypeVar")
    lines.append("from typing import Final, NotRequired, Unpack")
    lines.append("")
    lines.append("COMPONENT_MARK_ATTR: Final[str]")
    lines.append("COMPONENT_NAME_ATTR: Final[str]")
    lines.append("PROPS_MARK_ATTR: Final[str]")
    lines.append("")
    lines.append("class ExternalComponent:")
    lines.append("    module: str")
    lines.append("    name: str")
    lines.append("    default: bool")
    lines.append("    alias: str | None")
    lines.append("    @property")
    lines.append("    def import_name(self) -> str: ...")
    lines.append("    def __call__(self, *children: Child, **props: Unpack[HTMLProps]) -> Node: ...")
    lines.append("")
    lines.append("class JSExpr(str): ...")
    lines.append("")
    lines.append("class LocalComponent:")
    lines.append("    name: str")
    lines.append("    def __call__(self, *children: Child, **props: Unpack[HTMLProps]) -> Node: ...")
    lines.append("")
    lines.append("class Node:")
    lines.append("    tag: Any")
    lines.append("    props: dict[str, Any]")
    lines.append("    children: list[Any]")
    lines.append("")
    lines.append("class _Fragment: ...")
    lines.append("class _Slot: ...")
    lines.append("Fragment: _Fragment")
    lines.append("Slot: _Slot")
    lines.append("")
    lines.append("def js(expr: str) -> JSExpr: ...")
    lines.append("def external(module: str, name: str, *, default: bool = False, alias: str | None = None) -> ExternalComponent: ...")
    lines.append("def component(fn: Callable[..., Any]) -> Callable[..., Any]: ...")
    lines.append("def props(cls: type) -> type: ...")
    lines.append("")
    lines.append("class HTMLProps(TypedDict, total=False):")
    for name, type_ in HTML_PROPS:
        lines.append(f"    {name}: {type_}")
    lines.append("")
    lines.append("Child = Node | str | int | float | bool | None | JSExpr")
    lines.append("")
    lines.append("class TagCallable(Protocol):")
    lines.append("    def __call__(self, *children: Child, **props: Unpack[HTMLProps]) -> Node: ...")
    lines.append("")
    lines.append("class H:")
    lines.append("    def __call__(self, tag: Any, props: dict[str, Any] | None = None, *children: Child, **kwargs: Any) -> Node: ...")
    lines.append("    def __getattr__(self, tag: str) -> TagCallable: ...")
    lines.append("")
    for tag in HTML_TAGS + SVG_TAGS:
        if not tag.isidentifier() or tag in {"del"}:
            continue
        lines.append(f"    def {tag}(self, *children: Child, **props: Unpack[HTMLProps]) -> Node: ...")
    lines.append("")
    lines.append("h: H")
    lines.append("")
    lines.append("__all__: list[str]")
    lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "src" / "nestipy" / "web" / "ui" / "__init__.pyi"
    target.write_text(render(), encoding="utf-8")
