from __future__ import annotations

from typing import Iterable, Type

from .command_build import build, init
from .command_codegen import codegen, codegen_actions
from .command_dev import dev
from .command_pkg import add, install


def run_command(command_name: str, args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Dispatch the web subcommand by name."""
    if command_name == "web:init":
        init(args)
    elif command_name == "web:build":
        build(args, modules=modules)
    elif command_name == "web:dev":
        dev(args, modules=modules)
    elif command_name == "web:install":
        install(args)
    elif command_name == "web:add":
        add(args)
    elif command_name == "web:codegen":
        codegen(args, modules=modules)
    elif command_name == "web:actions":
        codegen_actions(args, modules=modules)
    else:
        raise RuntimeError(f"Unknown web command: {command_name}")


__all__ = [
    "add",
    "build",
    "codegen",
    "codegen_actions",
    "dev",
    "init",
    "install",
    "run_command",
]
