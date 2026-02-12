from __future__ import annotations

import inspect
import types
from dataclasses import dataclass
from dataclasses import is_dataclass
from typing import Any, Iterable, Annotated, get_args, get_origin

from pydantic import BaseModel

from nestipy.dynamic_module import DynamicModule
from nestipy.ioc.helper import ContainerHelper
from nestipy.metadata import CtxDepKey, ModuleMetadata, Reflect
from nestipy.web.actions import ACTION_METADATA


@dataclass(slots=True)
class ActionParam:
    name: str
    ts_type: str
    optional: bool


@dataclass(slots=True)
class ActionSpec:
    name: str
    params: list[ActionParam]
    return_type: str
    model_types: list[type]


def build_action_specs(modules: Iterable[type]) -> list[ActionSpec]:
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


def _build_action_spec(name: str, fn: Any) -> ActionSpec:
    sig = inspect.signature(fn)
    params: list[ActionParam] = []
    model_types: list[type] = []
    for param in sig.parameters.values():
        if param.name == "self":
            continue
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            ts_type = "unknown"
            optional = param.default is not inspect.Parameter.empty
            params.append(ActionParam(param.name, ts_type, optional))
            continue
        if _is_injected_param(annotation):
            continue
        ts_type = _py_to_ts(annotation)
        _collect_model_types(annotation, model_types)
        optional = param.default is not inspect.Parameter.empty or _is_optional(annotation)
        params.append(ActionParam(param.name, ts_type, optional))
    return_type = "unknown"
    if sig.return_annotation is not inspect.Signature.empty:
        return_type = _py_to_ts(sig.return_annotation)
        _collect_model_types(sig.return_annotation, model_types)
    return ActionSpec(name=name, params=params, return_type=return_type, model_types=model_types)


def _is_injected_param(annotation: Any) -> bool:
    _, dep_key = ContainerHelper.get_type_from_annotation(annotation)
    return dep_key.metadata.key != CtxDepKey.Service


def _is_optional(annotation: Any) -> bool:
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
    try:
        from typing import Union
    except Exception:
        return None
    return Union


def _unwrap_annotated(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        if args:
            return args[0]
    return annotation


def _py_to_ts(annotation: Any) -> str:
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


def _is_model_type(tp: Any) -> bool:
    if inspect.isclass(tp) and is_dataclass(tp):
        return True
    if inspect.isclass(tp) and issubclass(tp, BaseModel):
        return True
    if inspect.isclass(tp) and hasattr(tp, "__annotations__"):
        return True
    return False


def _collect_model_types(annotation: Any, out: list[type]) -> None:
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
    models: dict[str, type] = {}
    for spec in specs:
        for model in spec.model_types:
            models[model.__name__] = model
    return list(models.values())


def _render_model_interfaces(models: Iterable[type]) -> str:
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


def generate_actions_client_code(
    modules: Iterable[type], *, endpoint: str = "/_actions"
) -> str:
    specs = build_action_specs(modules)
    if not specs:
        return "\n".join(
            [
                "import { createActionClient, ActionResponse, ActionClientOptions } from './actions';",
                "",
                "export function createActions(_options: ActionClientOptions = {}) {",
                "  const call = createActionClient(_options);",
                "  return {",
                "    actions: {},",
                "    call,",
                "  };",
                "}",
                "",
            ]
        )

    grouped: dict[str, list[ActionSpec]] = {}
    for spec in specs:
        if "." in spec.name:
            group, method = spec.name.split(".", 1)
        else:
            group, method = "actions", spec.name
        grouped.setdefault(group, []).append(
            ActionSpec(
                name=method,
                params=spec.params,
                return_type=spec.return_type,
                model_types=spec.model_types,
            )
        )

    interfaces = _render_model_interfaces(_collect_models(specs))

    lines: list[str] = [
        "import { createActionClient, ActionResponse, ActionClientOptions } from './actions';",
        "",
    ]
    if interfaces:
        lines.append(interfaces)
    lines.append("export function createActions(options: ActionClientOptions = {}) {")
    lines.append("  const call = createActionClient({ ...options, endpoint: options.endpoint ?? '" + endpoint + "' });")
    lines.append("  return {")
    for group, actions in grouped.items():
        lines.append(f"    {group}: {{")
        for spec in actions:
            params = []
            args = []
            for param in spec.params:
                optional = "?" if param.optional else ""
                params.append(f"{param.name}{optional}: {param.ts_type}")
                args.append(param.name)
            param_list = ", ".join(params)
            args_list = ", ".join(args)
            lines.append(
                f"      {spec.name}: ({param_list}) => call<{spec.return_type}>(\"{group}.{spec.name}\", [{args_list}]),"
            )
        lines.append("    },")
    lines.append("    call,")
    lines.append("  };")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def write_actions_client_file(
    modules: Iterable[type],
    output: str,
    *,
    endpoint: str = "/_actions",
) -> None:
    code = generate_actions_client_code(modules, endpoint=endpoint)
    with open(output, "w", encoding="utf-8") as f:
        f.write(code)


__all__ = ["build_action_specs", "generate_actions_client_code", "write_actions_client_file"]
