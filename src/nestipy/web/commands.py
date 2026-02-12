from __future__ import annotations

import os
import time
from typing import Iterable, Type

from nestipy.web.config import WebConfig
from nestipy.web.compiler import compile_app
from nestipy.web.client import codegen_client, codegen_client_from_url


def _parse_args(args: Iterable[str]) -> dict[str, str | bool]:
    parsed: dict[str, str | bool] = {}
    args_list = list(args)
    i = 0
    while i < len(args_list):
        arg = args_list[i]
        if arg in {"--app", "--app-dir"} and i + 1 < len(args_list):
            parsed["app_dir"] = args_list[i + 1]
            i += 1
        elif arg in {"--out", "--out-dir"} and i + 1 < len(args_list):
            parsed["out_dir"] = args_list[i + 1]
            i += 1
        elif arg == "--clean":
            parsed["clean"] = True
        elif arg == "--watch":
            parsed["watch"] = True
        elif arg == "--target" and i + 1 < len(args_list):
            parsed["target"] = args_list[i + 1]
            i += 1
        elif arg == "--spec" and i + 1 < len(args_list):
            parsed["spec"] = args_list[i + 1]
            i += 1
        elif arg == "--output" and i + 1 < len(args_list):
            parsed["output"] = args_list[i + 1]
            i += 1
        elif arg == "--lang" and i + 1 < len(args_list):
            parsed["lang"] = args_list[i + 1]
            i += 1
        elif arg == "--class" and i + 1 < len(args_list):
            parsed["class_name"] = args_list[i + 1]
            i += 1
        elif arg == "--prefix" and i + 1 < len(args_list):
            parsed["prefix"] = args_list[i + 1]
            i += 1
        i += 1
    return parsed


def build(args: Iterable[str]) -> None:
    parsed = _parse_args(args)
    config = WebConfig(
        app_dir=str(parsed.get("app_dir", "app")),
        out_dir=str(parsed.get("out_dir", "web")),
        target=str(parsed.get("target", "vite")),
        clean=bool(parsed.get("clean", False)),
    )
    compile_app(config)
    _maybe_codegen_client(parsed, config)


def dev(args: Iterable[str]) -> None:
    parsed = _parse_args(args)
    config = WebConfig(
        app_dir=str(parsed.get("app_dir", "app")),
        out_dir=str(parsed.get("out_dir", "web")),
        target=str(parsed.get("target", "vite")),
        clean=bool(parsed.get("clean", False)),
    )
    app_dir = config.resolve_app_dir()
    last_state: dict[str, float] = {}

    def snapshot() -> dict[str, float]:
        state: dict[str, float] = {}
        for path in app_dir.rglob("*.py"):
            try:
                state[str(path)] = path.stat().st_mtime
            except FileNotFoundError:
                continue
        return state

    last_state = snapshot()
    compile_app(config)
    _maybe_codegen_client(parsed, config)
    try:
        while True:
            time.sleep(0.5)
            current = snapshot()
            if current != last_state:
                compile_app(config)
                _maybe_codegen_client(parsed, config)
                last_state = current
    except KeyboardInterrupt:
        return


def codegen(args: Iterable[str], modules: list[Type] | None = None) -> None:
    parsed = _parse_args(args)
    output = parsed.get("output")
    if not output:
        raise RuntimeError("Missing --output for web:codegen")

    language = str(parsed.get("lang", "python"))
    class_name = str(parsed.get("class_name", "ApiClient"))
    prefix = str(parsed.get("prefix", ""))

    spec_url = parsed.get("spec")
    if spec_url:
        codegen_client_from_url(str(spec_url), str(output), language=language, class_name=class_name)
        return

    if modules is None:
        raise RuntimeError("Modules are required to generate client without --spec")

    codegen_client(modules, str(output), language=language, class_name=class_name, prefix=prefix)


def run_command(command_name: str, args: Iterable[str], modules: list[Type] | None = None) -> None:
    if command_name == "web:build":
        build(args)
    elif command_name == "web:dev":
        dev(args)
    elif command_name == "web:codegen":
        codegen(args, modules=modules)
    else:
        raise RuntimeError(f"Unknown web command: {command_name}")


def _maybe_codegen_client(parsed: dict[str, str | bool], config: WebConfig) -> None:
    spec_url = parsed.get("spec")
    if not spec_url:
        return
    language = str(parsed.get("lang", "ts"))
    output = parsed.get("output")
    if not output:
        default_path = config.resolve_src_dir() / "api" / "client.ts"
        output = str(default_path)
    class_name = str(parsed.get("class_name", "ApiClient"))
    codegen_client_from_url(str(spec_url), str(output), language=language, class_name=class_name)
