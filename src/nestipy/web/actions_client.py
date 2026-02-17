from __future__ import annotations

import inspect
import json
import os
import types
import urllib.request
from dataclasses import dataclass
from dataclasses import is_dataclass
from typing import Any, Iterable, Annotated, get_args, get_origin, Callable

from pydantic import BaseModel

from nestipy.dynamic_module import DynamicModule
from nestipy.ioc.helper import ContainerHelper
from nestipy.metadata import CtxDepKey, ModuleMetadata, Reflect
from nestipy.web.actions import ACTION_METADATA


@dataclass(slots=True)
class ActionParam:
    """Describe a single action parameter for client generation."""
    name: str
    ts_type: str
    py_type: str
    optional: bool


@dataclass(slots=True)
class ActionSpec:
    """Describe a web action for client and schema generation."""
    name: str
    params: list[ActionParam]
    return_type: str
    return_py: str
    model_types: list[type]


def build_action_specs(modules: Iterable[type]) -> list[ActionSpec]:
    """Build action specifications by inspecting module providers/controllers."""
    specs: dict[str, ActionSpec] = {}
    for module in modules:
        if isinstance(module, DynamicModule):
            module = module.module
        providers = Reflect.get_metadata(module, ModuleMetadata.Providers, [])
        controllers = Reflect.get_metadata(module, ModuleMetadata.Controllers, [])
        for target in providers + controllers:
            if not inspect.isclass(target):
                continue
            for name, member in inspect.getmembers(target, predicate=callable):
                action_name = getattr(member, ACTION_METADATA, None)
                if not action_name:
                    continue
                if "." not in action_name:
                    action_name = f"{target.__name__}.{action_name}"
                spec = _build_action_spec(action_name, member)
                specs[action_name] = spec
    return list(specs.values())


def build_action_specs_from_registry(
    actions: dict[str, Callable[..., Any]],
) -> list[ActionSpec]:
    """Build action specs directly from a registry mapping."""
    specs: dict[str, ActionSpec] = {}
    for name, fn in actions.items():
        spec = _build_action_spec(name, fn)
        specs[name] = spec
    return list(specs.values())


def _build_action_spec(name: str, fn: Any) -> ActionSpec:
    """Build a single action spec from a callable signature."""
    sig = inspect.signature(fn)
    params: list[ActionParam] = []
    model_types: list[type] = []
    for param in sig.parameters.values():
        if param.name == "self":
            continue
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            ts_type = "unknown"
            py_type = "Any"
            optional = param.default is not inspect.Parameter.empty
            params.append(ActionParam(param.name, ts_type, py_type, optional))
            continue
        if _is_injected_param(annotation):
            continue
        ts_type = _py_to_ts(annotation)
        py_type = _py_to_py(annotation)
        _collect_model_types(annotation, model_types)
        optional = param.default is not inspect.Parameter.empty or _is_optional(annotation)
        params.append(ActionParam(param.name, ts_type, py_type, optional))
    return_type = "unknown"
    return_py = "Any"
    if sig.return_annotation is not inspect.Signature.empty:
        return_type = _py_to_ts(sig.return_annotation)
        return_py = _py_to_py(sig.return_annotation)
        _collect_model_types(sig.return_annotation, model_types)
    return ActionSpec(
        name=name,
        params=params,
        return_type=return_type,
        return_py=return_py,
        model_types=model_types,
    )


def _is_injected_param(annotation: Any) -> bool:
    """Return True for annotations that represent DI/context injections."""
    _, dep_key = ContainerHelper.get_type_from_annotation(annotation)
    return dep_key.metadata.key != "instance"


def _is_optional(annotation: Any) -> bool:
    """Return True if the annotation includes None in a union."""
    origin = get_origin(annotation)
    if origin is None:
        return False
    if origin is list or origin is dict or origin is tuple:
        return False
    if origin is _union_type() or origin is types.UnionType:
        args = get_args(annotation)
        return any(arg is type(None) for arg in args)
    return False


def _union_type() -> Any:
    """Return typing.Union in a version-safe way."""
    try:
        from typing import Union
    except Exception:
        return None
    return Union


def _unwrap_annotated(annotation: Any) -> Any:
    """Strip typing.Annotated wrappers when present."""
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        if args:
            return args[0]
    return annotation


def _py_to_ts(annotation: Any) -> str:
    """Convert a Python type annotation to a TypeScript type string."""
    annotation = _unwrap_annotated(annotation)
    origin = get_origin(annotation)
    if origin is not None:
        if origin in {list, tuple, set}:
            args = get_args(annotation)
            inner = _py_to_ts(args[0]) if args else "unknown"
            return f"Array<{inner}>"
        if origin is dict:
            args = get_args(annotation)
            value = _py_to_ts(args[1]) if len(args) > 1 else "unknown"
            return f"Record<string, {value}>"
        if origin is _union_type():
            args = get_args(annotation)
            parts = [_py_to_ts(a) for a in args if a is not type(None)]
            if any(a is type(None) for a in args):
                parts.append("null")
            return " | ".join(sorted(set(parts))) or "unknown"
        return "unknown"

    if annotation is str:
        return "string"
    if annotation is int or annotation is float:
        return "number"
    if annotation is bool:
        return "boolean"
    if annotation is None or annotation is type(None):
        return "null"
    if annotation is Any:
        return "unknown"
    if _is_model_type(annotation):
        return annotation.__name__
    return "unknown"


def _py_to_py(annotation: Any) -> str:
    """Convert a Python type annotation to a Python type string."""
    annotation = _unwrap_annotated(annotation)
    if isinstance(annotation, str):
        return annotation
    origin = get_origin(annotation)
    if origin is not None:
        if origin in {list, tuple, set}:
            args = get_args(annotation)
            inner = _py_to_py(args[0]) if args else "Any"
            container = "list" if origin is list else "tuple" if origin is tuple else "set"
            return f"{container}[{inner}]"
        if origin is dict:
            args = get_args(annotation)
            key = _py_to_py(args[0]) if args else "str"
            value = _py_to_py(args[1]) if len(args) > 1 else "Any"
            return f"dict[{key}, {value}]"
        if origin is _union_type() or origin is types.UnionType:
            args = get_args(annotation)
            parts = [_py_to_py(a) for a in args]
            return " | ".join(sorted(set(parts))) or "Any"
        return "Any"

    if annotation is str:
        return "str"
    if annotation is int:
        return "int"
    if annotation is float:
        return "float"
    if annotation is bool:
        return "bool"
    if annotation is None or annotation is type(None):
        return "None"
    if annotation is Any:
        return "Any"
    if _is_model_type(annotation):
        return annotation.__name__
    if inspect.isclass(annotation) and hasattr(annotation, "__name__"):
        return annotation.__name__
    return "Any"


def _is_model_type(tp: Any) -> bool:
    """Determine whether a type should be emitted as a TS interface."""
    if inspect.isclass(tp) and is_dataclass(tp):
        return True
    if inspect.isclass(tp) and issubclass(tp, BaseModel):
        return True
    if inspect.isclass(tp) and hasattr(tp, "__annotations__"):
        return True
    return False


def _collect_model_types(annotation: Any, out: list[type]) -> None:
    """Collect nested model types referenced by an annotation."""
    annotation = _unwrap_annotated(annotation)
    origin = get_origin(annotation)
    if origin in {list, tuple, dict, set}:
        for arg in get_args(annotation):
            _collect_model_types(arg, out)
        return
    if origin is _union_type() or origin is types.UnionType:
        for arg in get_args(annotation):
            _collect_model_types(arg, out)
        return
    if _is_model_type(annotation) and inspect.isclass(annotation):
        if annotation not in out:
            out.append(annotation)
            annotations = getattr(annotation, "__annotations__", {})
            for field_type in annotations.values():
                _collect_model_types(field_type, out)


def _collect_models(specs: Iterable[ActionSpec]) -> list[type]:
    """Deduplicate model types referenced across action specs."""
    models: dict[str, type] = {}
    for spec in specs:
        for model in spec.model_types:
            models[model.__name__] = model
    return list(models.values())


def _render_model_interfaces(models: Iterable[type]) -> str:
    """Render TypeScript interfaces for Python model types."""
    blocks: list[str] = []
    for model in models:
        annotations = getattr(model, "__annotations__", {})
        if not annotations:
            continue
        blocks.append(f"export interface {model.__name__} {{")
        for name, annotation in annotations.items():
            ts_type = _py_to_ts(annotation)
            optional = "?" if _is_optional(annotation) else ""
            blocks.append(f"  {name}{optional}: {ts_type};")
        blocks.append("}")
        blocks.append("")
    return "\n".join(blocks)


def _render_model_interfaces_from_schema(models: list[dict[str, Any]]) -> str:
    """Render TypeScript interfaces from a schema model list."""
    blocks: list[str] = []
    for model in models:
        name = model.get("name")
        fields = model.get("fields", [])
        if not name or not fields:
            continue
        blocks.append(f"export interface {name} {{")
        for field in fields:
            field_name = field.get("name")
            field_type = field.get("type", "unknown")
            optional = "?" if field.get("optional") else ""
            if field_name:
                blocks.append(f"  {field_name}{optional}: {field_type};")
        blocks.append("}")
        blocks.append("")
    return "\n".join(blocks)


def _schema_from_specs(specs: list[ActionSpec], endpoint: str) -> dict[str, Any]:
    """Build the JSON schema representation from action specs."""
    actions_schema: list[dict[str, Any]] = []
    for spec in specs:
        actions_schema.append(
            {
                "name": spec.name,
                "params": [
                    {
                        "name": param.name,
                        "type": param.ts_type,
                        "py_type": param.py_type,
                        "optional": param.optional,
                    }
                    for param in spec.params
                ],
                "return_type": spec.return_type,
                "return_py": spec.return_py,
            }
        )

    models_schema: list[dict[str, Any]] = []
    for model in _collect_models(specs):
        annotations = getattr(model, "__annotations__", {})
        if not annotations:
            continue
        fields = []
        for field_name, field_type in annotations.items():
            fields.append(
                {
                    "name": field_name,
                    "type": _py_to_ts(field_type),
                    "py_type": _py_to_py(field_type),
                    "optional": _is_optional(field_type),
                }
            )
        models_schema.append(
            {
                "name": model.__name__,
                "fields": fields,
            }
        )

    return {"endpoint": endpoint, "actions": actions_schema, "models": models_schema}


def build_actions_schema(modules: Iterable[type], *, endpoint: str = "/_actions") -> dict[str, Any]:
    """Build the actions schema from module metadata."""
    return _schema_from_specs(build_action_specs(modules), endpoint)


def build_actions_schema_from_registry(
    actions: dict[str, Callable[..., Any]], *, endpoint: str = "/_actions"
) -> dict[str, Any]:
    """Build the actions schema from an in-memory registry."""
    return _schema_from_specs(build_action_specs_from_registry(actions), endpoint)


def generate_actions_client_code_from_schema(schema: dict[str, Any]) -> str:
    """Generate a TypeScript actions client from schema JSON."""
    actions = schema.get("actions") or []
    endpoint = schema.get("endpoint", "/_actions")
    if not actions:
        return "\n".join(
            [
                "import { createActionClient, ActionResponse, ActionClientOptions, createActionMetaProvider } from './actions';",
                "",
                "export function createActions(options: ActionClientOptions = {}) {",
                "  const call = createActionClient({",
                "    ...options,",
                "    meta: options.meta ?? createActionMetaProvider(),",
                "  });",
                "  return {",
                "    actions: {},",
                "    call,",
                "  };",
                "}",
                "",
            ]
        )

    grouped: dict[str, list[ActionSpec]] = {}
    for action in actions:
        action_name = action.get("name")
        if not action_name:
            continue
        params = [
            ActionParam(
                name=param.get("name", "arg"),
                ts_type=param.get("type", "unknown"),
                py_type=param.get("py_type", "Any"),
                optional=bool(param.get("optional")),
            )
            for param in (action.get("params") or [])
        ]
        return_type = action.get("return_type", "unknown")
        if "." in action_name:
            group, method = action_name.split(".", 1)
        else:
            group, method = "actions", action_name
        grouped.setdefault(group, []).append(
            ActionSpec(
                name=method,
                params=params,
                return_type=return_type,
                return_py=action.get("return_py", "Any"),
                model_types=[],
            )
        )

    interfaces = _render_model_interfaces_from_schema(schema.get("models", []))

    lines: list[str] = [
        "import { createActionClient, ActionResponse, ActionClientOptions, createActionMetaProvider } from './actions';",
        "",
    ]
    if interfaces:
        lines.append(interfaces)
    lines.append("export function createActions(options: ActionClientOptions = {}) {")
    lines.append(
        "  const call = createActionClient({ ...options, endpoint: options.endpoint ?? '"
        + endpoint
        + "', meta: options.meta ?? createActionMetaProvider() });"
    )
    lines.append("  return {")
    for group, actions in grouped.items():
        lines.append(f"    {group}: {{")
        for spec in actions:
            if not spec.params:
                lines.append(
                    f"      {spec.name}: () => call<{spec.return_type}>(\"{group}.{spec.name}\"),"
                )
                continue
            shape_fields: list[str] = []
            for param in spec.params:
                opt = "?" if param.optional else ""
                shape_fields.append(f"{param.name}{opt}: {param.ts_type}")
            shape = "{ " + "; ".join(shape_fields) + " }"
            lines.append(
                f"      {spec.name}: (params: {shape}) => call<{spec.return_type}>(\"{group}.{spec.name}\", [], params as Record<string, unknown>),"
            )
        lines.append("    },")
    lines.append("    call,")
    lines.append("  };")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def generate_actions_client_code(
    modules: Iterable[type], *, endpoint: str = "/_actions"
) -> str:
    """Generate a TypeScript actions client from module metadata."""
    schema = build_actions_schema(modules, endpoint=endpoint)
    return generate_actions_client_code_from_schema(schema)


def codegen_actions_from_url(url: str, output: str) -> None:
    """Write a TypeScript actions client from a schema URL."""
    with urllib.request.urlopen(url) as response:
        schema = json.loads(response.read().decode("utf-8"))
    _ensure_parent(output)
    code = generate_actions_client_code_from_schema(schema)
    with open(output, "w", encoding="utf-8") as f:
        f.write(code)


def write_actions_client_file(
    modules: Iterable[type],
    output: str,
    *,
    endpoint: str = "/_actions",
) -> None:
    """Write a TypeScript actions client file from module metadata."""
    _ensure_parent(output)
    code = generate_actions_client_code(modules, endpoint=endpoint)
    with open(output, "w", encoding="utf-8") as f:
        f.write(code)


def generate_actions_types_code_from_schema(
    schema: dict[str, Any],
    *,
    class_name: str = "ActionsClient",
) -> str:
    """Generate Python protocol types from an actions schema."""
    actions = schema.get("actions") or []
    models = schema.get("models") or []

    def _pascal_case(value: str) -> str:
        parts = [p for p in value.replace(".", "_").split("_") if p]
        return "".join(p[:1].upper() + p[1:] for p in parts) or "Action"

    lines: list[str] = [
        "from __future__ import annotations",
        "",
        "from typing import Any, Protocol, TypedDict, NotRequired, Required, TypeVar, Generic, Callable",
        "",
        "T = TypeVar(\"T\")",
        "",
        "class ActionError(Protocol):",
        "    message: str",
        "    type: str",
        "",
        "class ActionResponse(Protocol, Generic[T]):",
        "    ok: bool",
        "    data: T | None",
        "    error: ActionError | None",
        "",
        "class JsPromise(Protocol, Generic[T]):",
        "    def then(",
        "        self,",
        "        on_fulfilled: Callable[[T], Any] | None = ...,",
        "        on_rejected: Callable[[Any], Any] | None = ...,",
        "    ) -> \"JsPromise[Any]\": ...",
        "",
    ]

    for model in models:
        name = model.get("name")
        fields = model.get("fields", [])
        if not name:
            continue
        lines.append(f"class {name}(Protocol):")
        if not fields:
            lines.append("    pass")
            lines.append("")
            continue
        for field in fields:
            field_name = field.get("name")
            if not field_name:
                continue
            field_type = field.get("py_type") or "Any"
            if field.get("optional"):
                field_type = f"{field_type} | None"
            lines.append(f"    {field_name}: {field_type}")
        lines.append("")

    grouped: dict[str, list[dict[str, Any]]] = {}
    for action in actions:
        name = action.get("name")
        if not name:
            continue
        if "." in name:
            group, method = name.split(".", 1)
        else:
            group, method = "actions", name
        grouped.setdefault(group, []).append({**action, "method": method})

    for group, group_actions in grouped.items():
        for action in group_actions:
            params = action.get("params") or []
            if not params:
                continue
            params_name = _pascal_case(f"{group}_{action['method']}_params")
            lines.append(f"class {params_name}(TypedDict, total=False):")
            for param in params:
                param_name = param.get("name") or "arg"
                param_type = param.get("py_type") or "Any"
                if param.get("optional"):
                    lines.append(f"    {param_name}: NotRequired[{param_type}]")
                else:
                    lines.append(f"    {param_name}: Required[{param_type}]")
            lines.append("")

        group_name = _pascal_case(group)
        lines.append(f"class {group_name}(Protocol):")
        if not group_actions:
            lines.append("    pass")
            lines.append("")
            continue
        for action in group_actions:
            return_py = action.get("return_py") or "Any"
            params = action.get("params") or []
            if params:
                params_name = _pascal_case(f"{group}_{action['method']}_params")
                lines.append(
                    f"    def {action['method']}(self, params: {params_name}) -> JsPromise[ActionResponse[{return_py}]]: ..."
                )
            else:
                lines.append(
                    f"    def {action['method']}(self) -> JsPromise[ActionResponse[{return_py}]]: ..."
                )
        lines.append("")

    lines.append(f"class {class_name}(Protocol):")
    if not grouped:
        lines.append("    pass")
    else:
        for group in grouped:
            group_name = _pascal_case(group)
            lines.append(f"    {group}: {group_name}")
        lines.append(
            "    call: Callable[..., JsPromise[ActionResponse[Any]]]"
        )
    lines.append("")
    return "\n".join(lines)


def generate_actions_types_code(
    modules: Iterable[type],
    *,
    class_name: str = "ActionsClient",
    endpoint: str = "/_actions",
) -> str:
    """Generate Python protocol types from module metadata."""
    schema = build_actions_schema(modules, endpoint=endpoint)
    return generate_actions_types_code_from_schema(schema, class_name=class_name)


def codegen_actions_types_from_url(url: str, output: str, *, class_name: str = "ActionsClient") -> None:
    """Write Python protocol types from a schema URL."""
    with urllib.request.urlopen(url) as response:
        schema = json.loads(response.read().decode("utf-8"))
    _ensure_parent(output)
    code = generate_actions_types_code_from_schema(schema, class_name=class_name)
    with open(output, "w", encoding="utf-8") as f:
        f.write(code)


def write_actions_types_file(
    modules: Iterable[type],
    output: str,
    *,
    class_name: str = "ActionsClient",
    endpoint: str = "/_actions",
) -> None:
    """Write Python protocol types from module metadata."""
    _ensure_parent(output)
    code = generate_actions_types_code(modules, class_name=class_name, endpoint=endpoint)
    with open(output, "w", encoding="utf-8") as f:
        f.write(code)


def _ensure_parent(output: str) -> None:
    """Ensure the output directory exists."""
    path = os.path.abspath(output)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


__all__ = [
    "build_action_specs",
    "build_action_specs_from_registry",
    "build_actions_schema",
    "build_actions_schema_from_registry",
    "generate_actions_client_code",
    "generate_actions_client_code_from_schema",
    "generate_actions_types_code",
    "generate_actions_types_code_from_schema",
    "codegen_actions_from_url",
    "codegen_actions_types_from_url",
    "write_actions_client_file",
    "write_actions_types_file",
]
